select *
from {{ ref('mart_daily_demand') }}
where armut_service_requests < 0
   or retail_order_lines < 0
   or retail_units_sold < 0
   or retail_gross_sales < 0
   or retail_net_sales < 0
