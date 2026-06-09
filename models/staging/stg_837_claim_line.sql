-- stg_837_claim_line | grain: one row per 837P service line. Typed select only.
with flattened as (
    {{ edi_flatten('service_lines', 'line', source_name='claims_837') }}
)
select
    {{ edi_get('', 'claim_id') }}                            as claim_id,
    {{ edi_get('line', 'line_sequence', 'integer') }}        as line_sequence,
    {{ edi_get('line', 'line_number') }}                     as source_line_number,
    {{ edi_get('line', 'procedure_code') }}                  as procedure_code,
    {{ edi_get('line', 'modifiers', 'array') }}              as modifiers,
    {{ edi_get('line', 'line_charge', 'decimal(18,2)') }}    as line_charge_amount,
    {{ edi_get('line', 'unit_type') }}                       as unit_type_code,
    {{ edi_get('line', 'units', 'decimal(12,3)') }}          as unit_count,
    {{ edi_get('line', 'diagnosis_pointers', 'array') }}     as diagnosis_pointers,
    {{ edi_get('line', 'service_date', 'date') }}            as service_date,
    {{ edi_get('line', 'rendering_provider_npi') }}          as line_rendering_provider_npi,
    {{ edi_get('line', 'line_control_number') }}             as line_control_number
from flattened
