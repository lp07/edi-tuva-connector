-- stg_835_claim_adjustment | grain: one row per claim-level CAS triplet.
-- Empty in synthetic data; element_struct pins the type so empty arrays do not
-- break inference. Typed select only.
with adjustments as (
    {{ edi_flatten('claim_level_adjustments', 'adj', source_name='remit_835',
                   element_struct='group_code varchar, reason_code varchar, amount varchar, quantity varchar') }}
)
select
    {{ edi_get('', 'claim_id') }}                      as claim_id,
    {{ edi_get('adj', 'group_code') }}                 as adjustment_group_code,
    {{ edi_get('adj', 'reason_code') }}                as adjustment_reason_code,
    {{ edi_get('adj', 'amount', 'decimal(18,2)') }}    as adjustment_amount,
    {{ edi_get('adj', 'quantity', 'decimal(12,3)') }}  as adjustment_quantity
from adjustments
