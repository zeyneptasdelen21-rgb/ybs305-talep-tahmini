
import argparse
import copy
import json
import os
from pathlib import Path

import requests


def auth_headers(api_key=None):
    session_id = os.environ.get("METABASE_SESSION_ID", "").strip()

    if session_id:
        return {"X-Metabase-Session": session_id}

    if api_key:
        return {"X-API-Key": api_key}

    raise RuntimeError(
        "Metabase oturumu veya API anahtari tanimli degil."
    )

ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS = ROOT / "scripts" / "metabase" / "definitions"

BASE_URL = os.environ.get(
    "METABASE_URL", "http://localhost:3000"
).rstrip("/")

DATABASE_NAME = "YBS305 Talep Tahmini"

OLD_TABLES = {
    13: ("analytics", "mart_monthly_demand"),
    14: ("analytics", "mart_retail_category_daily"),
}

OLD_FIELDS = {
    93: (13, "demand_month"),
    101: (14, "sale_date"),
    102: (14, "category"),
}


def api_get(path, api_key):
    response = requests.get(
        BASE_URL + path,
        headers=auth_headers(api_key),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def find_database(api_key):
    result = api_get("/api/database", api_key)

    matches = [
        db for db in result.get("data", [])
        if db.get("name") == DATABASE_NAME
        and db.get("engine") == "postgres"
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Proje veritabani bulunamadi veya birden fazla eslesme var."
        )

    return matches[0]["id"]


def find_tables(api_key, database_id):
    result = api_get(
        f"/api/database/{database_id}/metadata", api_key
    )

    table_map = {}

    for old_id, (schema, name) in OLD_TABLES.items():
        matches = [
            table for table in result.get("tables", [])
            if table.get("schema") == schema
            and table.get("name") == name
        ]

        if len(matches) != 1:
            raise RuntimeError(f"Tablo bulunamadi: {schema}.{name}")

        table_map[old_id] = matches[0]["id"]

    return table_map


def find_fields(api_key, table_map):
    field_map = {}
    metadata_cache = {}

    for old_id, (old_table_id, field_name) in OLD_FIELDS.items():
        new_table_id = table_map[old_table_id]

        if new_table_id not in metadata_cache:
            metadata_cache[new_table_id] = api_get(
                f"/api/table/{new_table_id}/query_metadata",
                api_key,
            )

        matches = [
            field
            for field in metadata_cache[new_table_id].get("fields", [])
            if field.get("name") == field_name
        ]

        if len(matches) != 1:
            raise RuntimeError(f"Alan bulunamadi: {field_name}")

        field_map[old_id] = matches[0]["id"]

    return field_map


def remap_ids(value, table_map, field_map):
    if isinstance(value, dict):
        result = {}

        for key, item in value.items():
            if key == "source-table" and isinstance(item, int):
                result[key] = table_map.get(item, item)
            else:
                result[key] = remap_ids(item, table_map, field_map)

        return result

    if isinstance(value, list):
        if (
            len(value) >= 2
            and value[0] == "field"
            and isinstance(value[1], int)
        ):
            result = copy.deepcopy(value)
            result[1] = field_map.get(result[1], result[1])

            for index in range(2, len(result)):
                result[index] = remap_ids(
                    result[index], table_map, field_map
                )

            return result

        return [
            remap_ids(item, table_map, field_map)
            for item in value
        ]

    return value


def load_definitions():
    dashboard_path = DEFINITIONS / "dashboard.json"

    with dashboard_path.open("r", encoding="utf-8-sig") as file:
        dashboard = json.load(file)

    cards = []

    for path in sorted(DEFINITIONS.glob("card-*.json")):
        with path.open("r", encoding="utf-8-sig") as file:
            cards.append(json.load(file))

    return dashboard, cards


def api_post(path, api_key, payload):
    response = requests.post(
        BASE_URL + path,
        headers=auth_headers(api_key),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def create_card(api_key, card, query):
    payload = {
        "name": card["name"],
        "display": card["display"],
        "dataset_query": query,
        "visualization_settings": card["visualization_settings"],
    }

    result = api_post("/api/card", api_key, payload)

    print(
        f"Kart olusturuldu: {result['name']} "
        f"(Yeni ID: {result['id']})"
    )

    return result["id"]


def create_all_cards(api_key, cards, database_id, table_map, field_map):
    existing_result = api_get("/api/card", api_key)

    if isinstance(existing_result, list):
        existing_cards = existing_result
    else:
        existing_cards = existing_result.get("data", [])

    created_cards = {}

    for card in cards:
        original_id = card["original_id"]
        name = "YBS305 AUTO - " + card["name"]

        matches = [
            item for item in existing_cards
            if item.get("name") == name
        ]

        if len(matches) > 1:
            raise RuntimeError(
                f"Ayni isimde birden fazla kart var: {name}"
            )

        if matches:
            new_id = matches[0]["id"]
            print(f"Mevcut kart: {name} (ID: {new_id})")
        else:
            query = remap_ids(
                card["dataset_query"],
                table_map,
                field_map,
            )
            query["database"] = database_id

            new_card = copy.deepcopy(card)
            new_card["name"] = name

            new_id = create_card(api_key, new_card, query)

        created_cards[original_id] = new_id

    return created_cards


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Gercek kurulum (henuz etkin degil)",
    )
    args = parser.parse_args()

    if args.apply:
        print("Kurulum modu secildi.")
        print("Kartlar hazirlandiktan sonra olusturulacak.")

    print("YBS305 - Metabase Dashboard Kurulumu")
    print("-" * 40)

    dashboard, cards = load_definitions()


    print("Dashboard:", dashboard["name"])
    print("Kart sayisi:", len(cards))
    print("Filtre sayisi:", len(dashboard["parameters"]))

    if len(cards) != 11:
        raise RuntimeError("Beklenen 11 kart bulunamadi.")

    api_key = os.environ.get("METABASE_API_KEY")

    if not api_key:
        raise RuntimeError("METABASE_API_KEY tanimlanmamis.")

    database_id = find_database(api_key)
    table_map = find_tables(api_key, database_id)
    field_map = find_fields(api_key, table_map)

    print("Veritabani ID:", database_id)

    for old_id, new_id in table_map.items():
        print(f"Tablo eslesmesi: {old_id} -> {new_id}")

    for old_id, new_id in field_map.items():
        print(f"Alan eslesmesi: {old_id} -> {new_id}")

    for card in cards:
        query = remap_ids(
            card["dataset_query"],
            table_map,
            field_map,
        )
        query["database"] = database_id

        print(
            f"Kart hazir: {card['original_id']} - "
            f"{card['name']}"
        )

    print("-" * 40)


    if args.apply:
        created_cards = create_all_cards(
            api_key,
            cards,
            database_id,
            table_map,
            field_map,
        )

        print("-" * 40)
        print("Hazirlanan kart sayisi:", len(created_cards))
        print("Kart ID eslesmeleri:", created_cards)
    else:
        print("Kontrol basarili. Hicbir degisiklik yapilmadi.")

if __name__ == "__main__":
    main()





