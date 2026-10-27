"""Export anonymous dbt mart data as CSV for the dashboard and hosted app."""
import csv
import os
from pathlib import Path
import psycopg2
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "app" / "data" / "mart_daily_demand.csv"
conn = psycopg2.connect(host=os.getenv("DBT_HOST", "localhost"), port=5432, dbname=os.getenv("DBT_DB", "retail_analytics"), user=os.getenv("DBT_USER", "analyst"), password=os.getenv("DBT_PASSWORD", "local_dev_only"))
try:
    with conn.cursor() as cur:
        cur.execute("select demand_date, demand_month, day_of_week, armut_service_requests, retail_order_lines, retail_units_sold, retail_gross_sales, retail_net_sales from analytics.mart_daily_demand order by demand_date")
        rows = cur.fetchall()
        headers = [d[0] for d in cur.description]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(headers); w.writerows(rows)
    print(f"Exported {len(rows)} rows to {OUT}")
finally:
    conn.close()
