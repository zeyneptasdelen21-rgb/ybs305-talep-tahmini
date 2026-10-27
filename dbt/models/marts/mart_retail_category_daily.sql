select
    sale_date,
    category,
    order_lines,
    units_sold,
    net_sales
from {{ ref('stg_retail_category_daily') }}
