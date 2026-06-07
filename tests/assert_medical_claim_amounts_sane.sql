-- Financial sanity on final adjudicated lines: allowed should not be less than
-- paid, paid should not exceed charge, and no amount should be negative.
select
    claim_id,
    claim_line_number,
    charge_amount,
    paid_amount,
    allowed_amount
from {{ ref('medical_claim') }}
where allowed_amount < paid_amount
   or paid_amount > charge_amount
   or paid_amount < 0
   or charge_amount < 0
