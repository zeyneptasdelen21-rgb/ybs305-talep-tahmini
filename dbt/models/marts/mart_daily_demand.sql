select
    demand_date,
    date_trunc('month', demand_date)::date as demand_month,
    extract(isodow from demand_date)::integer as day_of_week,
    armut_service_requests,
    retail_order_lines,
    retail_units_sold,
    retail_gross_sales,
    retail_net_sales
from {{ ref('int_daily_demand') }}
