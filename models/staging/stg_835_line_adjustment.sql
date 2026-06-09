-- stg_835_line_adjustment | grain: one row per line-level CAS triplet.
-- Two-level flatten: service_lines then line_adjustments. Typed select only.
with lines as (
    {{ edi_flatten('service_lines', 'line', source_name='remit_835') }}
),
adjustments as (
    {{ edi_flatten('line_adjustments', 'adj', from_rel='lines', parent='line',
                   element_struct='group_code varchar, reason_code varchar, amount varchar, quantity varchar') }}
)
select
    {{ edi_get('', 'claim_id') }}                      as claim_id,
    {{ edi_get('line', 'line_sequence', 'integer') }}  as line_sequence,
    {{ edi_get('adj', 'group_code') }}                 as adjustment_group_code,
    {{ edi_get('adj', 'reason_code') }}                as adjustment_reason_code,
    {{ edi_get('adj', 'amount', 'decimal(18,2)') }}    as adjustment_amount,
    {{ edi_get('adj', 'quantity', 'decimal(12,3)') }}  as adjustment_quantity
from adjustments
