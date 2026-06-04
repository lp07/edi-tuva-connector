-- stg_837_diagnosis
-- Grain: one row per 837P claim diagnosis.
-- Flattens the claim's own diagnoses[] array. diagnosis_sequence is the ordinal
-- position in the HI segment; SV1-07 pointers on a service line reference this
-- number. Pointer-to-code resolution is an intermediate-layer join.

with source as (

    select claim_id, diagnoses
    from {{ source('edi_parsed', 'claims_837') }}

),

flattened as (

    select
        claim_id,
        unnest(diagnoses) as dx
    from source

)

select
    cast(claim_id as varchar)            as claim_id,
    try_cast(dx.sequence as integer)         as diagnosis_sequence,
    cast(dx.qualifier as varchar)        as diagnosis_qualifier_code,
    cast(dx.code as varchar)             as diagnosis_code
from flattened
