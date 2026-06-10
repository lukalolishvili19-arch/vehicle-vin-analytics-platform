-- Assert grade is within 0.0–5.0 bounds
-- TODO: Implement assert_grade_bounds

select *
from {{ ref('fct_vehicle_inventory') }}
where grade is not null and (grade < 0 or grade > 5)
