select event_date, sum(service_requests)::integer as service_requests
from {{ ref('stg_armut_daily') }}
group by event_date
