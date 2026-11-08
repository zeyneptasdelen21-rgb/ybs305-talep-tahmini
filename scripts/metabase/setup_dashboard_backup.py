
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "exports"

TABLES = {
    13: "analytics.mart_monthly_demand",
    14: "analytics.mart_retail_category_daily",
}

def main():
    print("YBS305 - Metabase Dashboard Kurulumu")
    print("-" * 40)

    dashboard_file = EXPORT_DIR / "dashboard-raw.json"

    if not dashboard_file.exists():
        print("Dashboard JSON dosyasi bulunamadi.")
        return

    with dashboard_file.open("r", encoding="utf-8-sig") as f:
        dashboard = json.load(f)

    print("Dashboard:", dashboard["name"])
    print("Kart sayisi:", len(dashboard["dashcards"]))
    print("Filtre sayisi:", len(dashboard["parameters"]))

    for table_id, table_name in TABLES.items():
        print(f"Kaynak tablo {table_id}: {table_name}")

if __name__ == "__main__":
    main()

import requests

def test_metabase_connection():
    url = "http://localhost:3000/api/health"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print("Metabase baglantisi:", response.json())
    except requests.RequestException as error:
        print("Metabase baglanti hatasi:", error)

test_metabase_connection()


import os

def find_project_database():
    api_key = os.environ.get("METABASE_API_KEY")

    if not api_key:
        print("METABASE_API_KEY bulunamadi.")
        return

    url = "http://localhost:3000/api/database"
    headers = {"X-API-Key": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        databases = response.json().get("data", [])

        for database in databases:
            if (
                database["name"] == "YBS305 Talep Tahmini"
                and database["engine"] == "postgres"
            ):
                print("Proje veritabani bulundu.")
                print("Veritabani ID:", database["id"])
                return database["id"]

        print("Proje veritabani bulunamadi.")

    except requests.RequestException as error:
        print("API hatasi:", error)


find_project_database()


def find_project_tables(database_id):
    api_key = os.environ.get("METABASE_API_KEY")

    if not api_key or database_id is None:
        print("API anahtari veya veritabani ID eksik.")
        return {}

    url = f"http://localhost:3000/api/database/{database_id}/metadata"

    try:
        response = requests.get(
            url,
            headers={"X-API-Key": api_key},
            timeout=20
        )
        response.raise_for_status()

        expected_tables = {
            "mart_monthly_demand",
            "mart_retail_category_daily"
        }

        found = {}

        for table in response.json().get("tables", []):
            if (
                table.get("schema") == "analytics"
                and table.get("name") in expected_tables
            ):
                found[table["name"]] = table["id"]

        for name, table_id in found.items():
            print(f"Tablo bulundu: {name} (ID: {table_id})")

        if len(found) != len(expected_tables):
            print("Uyari: Bazi kaynak tablolar bulunamadi.")

        return found

    except requests.RequestException as error:
        print("Tablo sorgulama hatasi:", error)
        return {}


database_id = find_project_database()
find_project_tables(database_id)
