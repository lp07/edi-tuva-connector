-- 835 claim paid (CLP04) must equal the sum of its service line paid (SVC03),
-- given this source carries no claim-level paid adjustments. Catches join or
-- aggregation drift between the claim payment header and its lines.
with line_sums as (
    select claim_id, sum(line_paid_amount) as line_paid_total
    from {{ ref('stg_835_claim_line') }}
    group by claim_id
)
select
    p.claim_id,
    p.claim_paid_amount,
    s.line_paid_total
from {{ ref('stg_835_claim') }} p
join line_sums s on p.claim_id = s.claim_id
where p.claim_paid_amount <> s.line_paid_total
