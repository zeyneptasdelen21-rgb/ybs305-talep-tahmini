select
    demand_month,
    sum(armut_service_requests)::integer as armut_service_requests,
    sum(retail_order_lines)::integer as retail_order_lines,
    sum(retail_units_sold)::integer as retail_units_sold,
    sum(retail_gross_sales)::numeric(14, 2) as retail_gross_sales,
    sum(retail_net_sales)::numeric(14, 2) as retail_net_sales,
    count(*)::integer as calendar_days
from {{ ref('mart_daily_demand') }}
group by demand_month
