select
    sale_date::date as sale_date,
    category::varchar(100) as category,
    order_lines::integer as order_lines,
    units_sold::integer as units_sold,
    net_sales::numeric(14, 2) as net_sales
from {{ ref('retail_category_daily') }}
