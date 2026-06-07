-- Positional join validation. Because the source writes no per-line REF*6R, the
-- 837 and 835 lines are aligned on (claim_id, line_sequence). At each aligned
-- position the submitted procedure must equal the paid procedure. Any row here
-- means the positional assumption broke for that claim.
select
    a.claim_id,
    a.line_sequence,
    a.procedure_code as procedure_837,
    b.procedure_code as procedure_835
from {{ ref('stg_837_claim_line') }} a
join {{ ref('stg_835_claim_line') }} b
    on a.claim_id = b.claim_id
    and a.line_sequence = b.line_sequence
where coalesce(a.procedure_code, '') <> coalesce(b.procedure_code, '')
