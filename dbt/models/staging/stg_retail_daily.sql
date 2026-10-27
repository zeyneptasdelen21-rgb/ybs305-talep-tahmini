select
    sale_date::date as sale_date,
    order_lines::integer as order_lines,
    units_sold::integer as units_sold,
    gross_sales::numeric(14, 2) as gross_sales,
    net_sales::numeric(14, 2) as net_sales
from {{ ref('retail_daily') }}
