-- int_835_line_financials
-- Grain: one row per paid claim line that has adjustments.
-- Splits line-level CAS patient-responsibility amounts into Tuva's cost-sharing
-- buckets using standard CARC reason codes within group PR:
--   reason 1 = deductible, 2 = coinsurance, 3 = copayment.
-- Other PR reasons (for example 96 non-covered) and all CO contractual amounts
-- are intentionally excluded here; they are not member cost sharing.

with adj as (

    select
        claim_id,
        line_sequence,
        adjustment_group_code,
        adjustment_reason_code,
        adjustment_amount
    from {{ ref('stg_835_line_adjustment') }}

)

select
    claim_id,
    line_sequence,
    sum(case when adjustment_group_code = 'PR' and adjustment_reason_code = '1' then adjustment_amount end) as deductible_amount,
    sum(case when adjustment_group_code = 'PR' and adjustment_reason_code = '2' then adjustment_amount end) as coinsurance_amount,
    sum(case when adjustment_group_code = 'PR' and adjustment_reason_code = '3' then adjustment_amount end) as copayment_amount
from adj
group by claim_id, line_sequence
