-- Assert VIN uniqueness in marts
-- TODO: Implement assert_unique_vin

select vin, count(*) as cnt
from {{ ref('fct_vehicle_inventory') }}
group by vin
having count(*) > 1
