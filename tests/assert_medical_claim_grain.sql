-- Primary key uniqueness on the Tuva contract grain.
select
    claim_id,
    claim_line_number,
    data_source,
    count(*) as n
from {{ ref('medical_claim') }}
group by claim_id, claim_line_number, data_source
having count(*) > 1
