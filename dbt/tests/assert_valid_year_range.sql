-- Assert year is within valid range
-- TODO: Implement assert_valid_year_range

select *
from {{ ref('fct_vehicle_inventory') }}
where year < 1990 or year > 2030
