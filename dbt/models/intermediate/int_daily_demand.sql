select
    coalesce(a.event_date, r.sale_date) as demand_date,
    case
        when a.event_date is null then null
        else a.service_requests
    end::integer as armut_service_requests,
    (a.event_date is not null) as armut_data_available,
    coalesce(r.order_lines, 0)::integer as retail_order_lines,
    coalesce(r.units_sold, 0)::integer as retail_units_sold,
    coalesce(r.gross_sales, 0)::numeric(14, 2) as retail_gross_sales,
    coalesce(r.net_sales, 0)::numeric(14, 2) as retail_net_sales
from {{ ref('int_armut_demand_by_day') }} a
full outer join {{ ref('stg_retail_daily') }} r
    on a.event_date = r.sale_date
