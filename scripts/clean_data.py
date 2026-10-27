"""Clean source files locally and create anonymous daily aggregates for dbt seeds."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SEEDS = ROOT / "dbt" / "seeds"
REPORT = ROOT / "data" / "processed" / "cleaning_report.json"
START, END = date(2024, 1, 1), date(2024, 12, 31)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    armut_source = RAW / "armut_data.csv"
    retail_source = RAW / "perakende_satis.xlsx"
    if not armut_source.exists() or not retail_source.exists():
        raise FileNotFoundError("Place both source files in data/raw/; see README.md")

    armut_counts: Counter = Counter()
    armut_input_rows = armut_bad_dates = armut_duplicates = 0
    seen_armut: set[tuple[str, ...]] = set()
    with armut_source.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            armut_input_rows += 1
            key = tuple(row.get(k, "") for k in ("UserId", "ServiceId", "CategoryId", "CreateDate"))
            if key in seen_armut:
                armut_duplicates += 1
                continue
            seen_armut.add(key)
            try:
                day = date.fromisoformat(row["CreateDate"][:10])
                category = str(int(row["CategoryId"]))
            except (ValueError, TypeError, KeyError):
                armut_bad_dates += 1
                continue
            if START <= day <= END:
                armut_counts[(day.isoformat(), category)] += 1

    wb = openpyxl.load_workbook(retail_source, read_only=True, data_only=True)
    ws = wb.active
    it = ws.iter_rows(values_only=True)
    headers = next(it)
    required = {"Tarih", "Kategori", "Miktar", "BirimFiyat", "IndirimOrani"}
    if not required.issubset(set(headers)):
        raise ValueError(f"Missing retail columns: {sorted(required - set(headers))}")
    idx = {name: headers.index(name) for name in required}
    retail_daily = defaultdict(lambda: {"order_lines": 0, "units": 0, "gross_sales": 0.0, "net_sales": 0.0})
    retail_category = defaultdict(lambda: {"order_lines": 0, "units": 0, "net_sales": 0.0})
    retail_input_rows = retail_bad_rows = retail_duplicates = 0
    seen_retail: set[tuple] = set()
    for row in it:
        retail_input_rows += 1
        try:
            day = row[idx["Tarih"]]
            if isinstance(day, str):
                day = date.fromisoformat(day[:10])
            elif hasattr(day, "date"):
                day = day.date()
            category = str(row[idx["Kategori"]]).strip()
            units = int(row[idx["Miktar"]])
            price = float(row[idx["BirimFiyat"]])
            discount = float(row[idx["IndirimOrani"]] or 0)
            if not category or units < 0 or price < 0 or not 0 <= discount <= 1:
                raise ValueError("invalid value")
        except (ValueError, TypeError, IndexError):
            retail_bad_rows += 1
            continue
        key = tuple(row)
        if key in seen_retail:
            retail_duplicates += 1
            continue
        seen_retail.add(key)
        if not START <= day <= END:
            continue
        date_key = day.isoformat()
        gross = units * price
        net = gross * (1 - discount)
        retail_daily[date_key]["order_lines"] += 1
        retail_daily[date_key]["units"] += units
        retail_daily[date_key]["gross_sales"] += gross
        retail_daily[date_key]["net_sales"] += net
        retail_category[(date_key, category)]["order_lines"] += 1
        retail_category[(date_key, category)]["units"] += units
        retail_category[(date_key, category)]["net_sales"] += net

    # Full calendar makes unobserved days explicit as zero for exploratory alignment.
    calendar = [START + timedelta(days=n) for n in range((END - START).days + 1)]
    armut_rows = []
    retail_rows = []
    retail_cat_rows = []
    for day in calendar:
        d = day.isoformat()
        cats = sorted((cat for (dt, cat) in armut_counts if dt == d), key=int)
        if cats:
            armut_rows.extend({"event_date": d, "category_id": cat, "service_requests": armut_counts[(d, cat)]} for cat in cats)
        else:
            armut_rows.append({"event_date": d, "category_id": "unknown", "service_requests": 0})
        x = retail_daily[d]
        retail_rows.append({"sale_date": d, "order_lines": x["order_lines"], "units_sold": x["units"], "gross_sales": round(x["gross_sales"], 2), "net_sales": round(x["net_sales"], 2)})
        cat_keys = sorted((cat for (dt, cat) in retail_category if dt == d))
        for cat in cat_keys:
            y = retail_category[(d, cat)]
            retail_cat_rows.append({"sale_date": d, "category": cat, "order_lines": y["order_lines"], "units_sold": y["units"], "net_sales": round(y["net_sales"], 2)})

    write_csv(SEEDS / "armut_daily.csv", armut_rows, ["event_date", "category_id", "service_requests"])
    write_csv(SEEDS / "retail_daily.csv", retail_rows, ["sale_date", "order_lines", "units_sold", "gross_sales", "net_sales"])
    write_csv(SEEDS / "retail_category_daily.csv", retail_cat_rows, ["sale_date", "category", "order_lines", "units_sold", "net_sales"])
    report = {
        "scope": "calendar year 2024",
        "sources": {
            "armut": {"input_rows": armut_input_rows, "duplicate_rows_removed": armut_duplicates, "invalid_rows_removed": armut_bad_dates, "rows_in_2024": sum(armut_counts.values()), "output_aggregate_rows": len(armut_rows), "identifier_columns_removed": ["UserId", "ServiceId"]},
            "retail": {"input_rows": retail_input_rows, "duplicate_rows_removed": retail_duplicates, "invalid_rows_removed": retail_bad_rows, "rows_in_2024": sum(v["order_lines"] for v in retail_daily.values()), "output_daily_rows": len(retail_rows), "identifier_columns_removed": ["SiparisID", "Musteri_ID", "Sehir", "Bolge", "Kanal", "Urun", "BirimFiyat", "Maliyet"]}
        },
        "notes": ["Outputs are aggregates; user/customer identifiers are excluded.", "Days with no source rows are represented as zero; verify whether source coverage means true zero demand.", "Armut category_id values remain numeric source codes; no category-name mapping was supplied."]
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
