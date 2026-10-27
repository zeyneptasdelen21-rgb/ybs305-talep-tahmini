select
    event_date::date as event_date,
    category_id::varchar(20) as category_id,
    service_requests::integer as service_requests
from {{ ref('armut_daily') }}
