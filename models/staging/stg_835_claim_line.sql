-- stg_835_claim_line | grain: one row per 835 service line. Typed select only.
with flattened as (
    {{ edi_flatten('service_lines', 'line', source_name='remit_835') }}
)
select
    {{ edi_get('', 'claim_id') }}                          as claim_id,
    {{ edi_get('line', 'line_sequence', 'integer') }}      as line_sequence,
    {{ edi_get('line', 'procedure_code') }}                as procedure_code,
    {{ edi_get('line', 'modifiers', 'array') }}            as modifiers,
    {{ edi_get('line', 'line_charge', 'decimal(18,2)') }}  as line_charge_amount,
    {{ edi_get('line', 'line_paid', 'decimal(18,2)') }}    as line_paid_amount,
    {{ edi_get('line', 'units_paid', 'decimal(12,3)') }}   as paid_unit_count,
    {{ edi_get('line', 'service_date', 'date') }}          as service_date,
    {{ edi_get('line', 'line_control_number') }}           as line_control_number,
    {{ edi_get('line', 'remark_codes', 'array') }}         as remark_codes
from flattened
