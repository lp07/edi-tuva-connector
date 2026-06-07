-- 837 claim total charge (CLM02) must equal the sum of its service line charges
-- (SV1-02). Catches parse or aggregation errors between header and lines.
with line_sums as (
    select claim_id, sum(line_charge_amount) as line_charge_total
    from {{ ref('stg_837_claim_line') }}
    group by claim_id
)
select
    c.claim_id,
    c.total_charge_amount,
    l.line_charge_total
from {{ ref('stg_837_claim') }} c
join line_sums l on c.claim_id = l.claim_id
where c.total_charge_amount <> l.line_charge_total
