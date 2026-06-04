-- stg_837_claim_line
-- Grain: one row per 837P service line.
-- Flattens the claim's own service_lines[] array and casts. modifiers and
-- diagnosis_pointers stay as typed varchar lists; pointer resolution to actual
-- diagnosis codes happens in intermediate against stg_837_diagnosis.

with source as (

    select claim_id, service_lines
    from {{ source('edi_parsed', 'claims_837') }}

),

flattened as (

    select
        claim_id,
        unnest(service_lines) as line
    from source

)

select
    cast(claim_id as varchar)                          as claim_id,
    try_cast(line.line_sequence as integer)                as line_sequence,
    cast(line.line_number as varchar)                  as source_line_number,
    cast(line.procedure_code as varchar)               as procedure_code,
    cast(line.modifiers as varchar[])                  as modifiers,
    try_cast(line.line_charge as decimal(18, 2))           as line_charge_amount,
    cast(line.unit_type as varchar)                    as unit_type_code,
    try_cast(line.units as decimal(12, 3))                 as unit_count,
    cast(line.diagnosis_pointers as varchar[])         as diagnosis_pointers,
    try_strptime(line.service_date, '%Y%m%d')::date    as service_date,
    cast(line.rendering_provider_npi as varchar)       as line_rendering_provider_npi,
    cast(line.line_control_number as varchar)          as line_control_number
from flattened
