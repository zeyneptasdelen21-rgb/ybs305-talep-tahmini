from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SEEDS = ROOT / "dbt" / "seeds"
REPORT = ROOT / "data" / "processed" / "cleaning_report.json"
START, END = date(2024, 1, 1), date(2024, 12, 31)


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")


def main() -> None:
    armut_source = RAW / "armut_data.csv"
    retail_source = RAW / "perakende_satis.xlsx"
    if not armut_source.exists() or not retail_source.exists():
        raise FileNotFoundError("Place both source files in data/raw/; expected armut_data.csv and perakende_satis.xlsx")

    # Armut: inspect missing values and exact duplicate records with pandas.
    armut = pd.read_csv(armut_source, encoding="utf-8-sig")
    armut_required = ["UserId", "ServiceId", "CategoryId", "CreateDate"]
    if not set(armut_required).issubset(armut.columns):
        raise ValueError(f"Armut file is missing columns: {sorted(set(armut_required) - set(armut.columns))}")
    armut_input_rows = len(armut)
    armut_missing = int(armut[armut_required].isna().sum().sum())
    armut_duplicate_rows = int(armut.duplicated(subset=armut_required).sum())
    armut = armut.drop_duplicates(subset=armut_required).copy()
    armut["_date"] = pd.to_datetime(armut["CreateDate"], errors="coerce")
    armut["_category"] = pd.to_numeric(armut["CategoryId"], errors="coerce")
    armut_invalid_mask = armut["_date"].isna() | armut["_category"].isna()
    armut_invalid_rows = int(armut_invalid_mask.sum())
    armut = armut.loc[~armut_invalid_mask].copy()
    armut["_day"] = armut["_date"].dt.date
    armut = armut.loc[armut["_day"].between(START, END)].copy()
    armut["event_date"] = armut["_day"].astype(str)
    armut["category_id"] = armut["_category"].astype("int64").astype(str)
    armut_daily = (
        armut.groupby(["event_date", "category_id"], as_index=False)
        .size()
        .rename(columns={"size": "service_requests"})
    )
    armut_rows_in_year = int(armut_daily["service_requests"].sum())
    armut_source_date_start = str(armut["event_date"].min())
    armut_source_date_end = str(armut["event_date"].max())
    armut_observed_source_dates = int(armut["event_date"].nunique())
    armut_category_ids = sorted(armut_daily["category_id"].unique(), key=int)
    armut_calendar = pd.date_range(armut_source_date_start, armut_source_date_end, freq="D").strftime("%Y-%m-%d")
    armut_complete_grid = pd.MultiIndex.from_product(
        [armut_calendar, armut_category_ids],
        names=["event_date", "category_id"],
    ).to_frame(index=False)
    armut_observed_groups = len(armut_daily)
    armut_daily = armut_complete_grid.merge(
        armut_daily,
        on=["event_date", "category_id"],
        how="left",
    )
    armut_daily["service_requests"] = armut_daily["service_requests"].fillna(0).astype("int64")
    armut_missing_category_days_filled_zero = len(armut_daily) - armut_observed_groups

    # Retail: inspect missing values, remove exact duplicates, and validate values.
    retail = pd.read_excel(retail_source)
    retail_required = ["Tarih", "Kategori", "Miktar", "BirimFiyat", "IndirimOrani"]
    if not set(retail_required).issubset(retail.columns):
        raise ValueError(f"Retail file is missing columns: {sorted(set(retail_required) - set(retail.columns))}")
    retail_input_rows = len(retail)
    retail_missing_by_column = {
        str(column): int(count)
        for column, count in retail[retail_required].isna().sum().items()
    }
    retail_missing_cells = int(sum(retail_missing_by_column.values()))
    retail_duplicate_rows = int(retail.duplicated().sum())
    retail = retail.drop_duplicates().copy()

    retail["_date"] = pd.to_datetime(retail["Tarih"], errors="coerce")
    retail["_category"] = retail["Kategori"].astype("string").str.strip()
    retail["_units"] = pd.to_numeric(retail["Miktar"], errors="coerce")
    retail["_price"] = pd.to_numeric(retail["BirimFiyat"], errors="coerce")
    retail["_discount"] = pd.to_numeric(retail["IndirimOrani"], errors="coerce").fillna(0)
    # Missing discount means no recorded discount; missing required values are excluded below.
    retail_invalid_mask = (
        retail["_date"].isna()
        | retail["_category"].isna()
        | retail["_category"].eq("")
        | retail["_units"].isna()
        | retail["_price"].isna()
        | (retail["_units"] < 0)
        | (retail["_price"] < 0)
        | ~retail["_discount"].between(0, 1)
    )
    retail_negative_prices = int((retail["_price"] < 0).sum())
    retail_negative_units = int((retail["_units"] < 0).sum())
    retail_invalid_rows = int(retail_invalid_mask.sum())
    retail = retail.loc[~retail_invalid_mask].copy()
    retail["_day"] = retail["_date"].dt.date
    retail = retail.loc[retail["_day"].between(START, END)].copy()
    retail["sale_date"] = retail["_day"].astype(str)
    retail["order_lines"] = 1
    retail["units_sold"] = retail["_units"].astype("int64")
    retail["gross_sales"] = retail["units_sold"] * retail["_price"]
    retail["net_sales"] = retail["gross_sales"] * (1 - retail["_discount"])

    retail_daily = (
        retail.groupby("sale_date", as_index=False)
        .agg(
            order_lines=("order_lines", "sum"),
            units_sold=("units_sold", "sum"),
            gross_sales=("gross_sales", "sum"),
            net_sales=("net_sales", "sum"),
        )
    )
    retail_category_daily = (
        retail.groupby(["sale_date", "_category"], as_index=False)
        .agg(
            order_lines=("order_lines", "sum"),
            units_sold=("units_sold", "sum"),
            net_sales=("net_sales", "sum"),
        )
        .rename(columns={"_category": "category"})
    )
    retail_rows_in_year = int(retail["order_lines"].sum())

    # Add every day of 2024 to the daily series. A missing source date is recorded as zero.
    calendar = pd.date_range(START, END, freq="D").strftime("%Y-%m-%d")
    retail_daily = retail_daily.set_index("sale_date").reindex(calendar, fill_value=0)
    retail_daily.index.name = "sale_date"
    retail_daily = retail_daily.reset_index()
    retail_daily["gross_sales"] = retail_daily["gross_sales"].round(2)
    retail_daily["net_sales"] = retail_daily["net_sales"].round(2)


    write_csv(SEEDS / "armut_daily.csv", armut_daily[["event_date", "category_id", "service_requests"]])
    write_csv(SEEDS / "retail_daily.csv", retail_daily[["sale_date", "order_lines", "units_sold", "gross_sales", "net_sales"]])
    write_csv(SEEDS / "retail_category_daily.csv", retail_category_daily[["sale_date", "category", "order_lines", "units_sold", "net_sales"]])

    report = {
        "scope": "calendar year 2024",
        "method": "pandas; missing values, exact duplicates, dates and numeric ranges inspected",
        "sources": {
            "armut": {
                "input_rows": armut_input_rows,
                "missing_required_cells": armut_missing,
                "duplicate_rows_removed": armut_duplicate_rows,
                "invalid_rows_removed": armut_invalid_rows,
                "rows_in_2024": armut_rows_in_year,
                "source_date_start": armut_source_date_start,
                "source_date_end": armut_source_date_end,
                "observed_source_dates": armut_observed_source_dates,
                "category_ids": armut_category_ids,
                "missing_category_date_pairs_filled_zero": armut_missing_category_days_filled_zero,
                "output_aggregate_rows": len(armut_daily),
                "identifier_columns_removed": ["UserId", "ServiceId"],
            },
            "retail": {
                "input_rows": retail_input_rows,
                "missing_cells_by_required_column": retail_missing_by_column,
                "missing_required_cells": retail_missing_cells,
                "duplicate_rows_removed": retail_duplicate_rows,
                "negative_price_rows": retail_negative_prices,
                "negative_unit_rows": retail_negative_units,
                "invalid_rows_removed": retail_invalid_rows,
                "rows_in_2024": retail_rows_in_year,
                "output_daily_rows": len(retail_daily),
                "identifier_columns_removed": ["SiparisID", "Musteri_ID", "Sehir", "Bolge", "Kanal", "Urun", "BirimFiyat", "Maliyet"],
            },
        },
        "notes": [
            "Outputs are aggregates; user/customer identifiers are excluded.",
            "A missing discount is treated as 0 (no recorded discount); rows missing other required values are excluded.",
            "Armut dates outside the observed 2024 source coverage are not generated.",
            "Within Armut source coverage, missing category-date pairs are zero-filled for category codes present in the source.",
            "Armut category_id values remain numeric source codes; no category-name mapping was supplied.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

