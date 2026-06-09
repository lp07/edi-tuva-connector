-- stg_837_diagnosis | grain: one row per 837P claim diagnosis. Typed select only.
with flattened as (
    {{ edi_flatten('diagnoses', 'dx', source_name='claims_837') }}
)
select
    {{ edi_get('', 'claim_id') }}                  as claim_id,
    {{ edi_get('dx', 'sequence', 'integer') }}     as diagnosis_sequence,
    {{ edi_get('dx', 'qualifier') }}               as diagnosis_qualifier_code,
    {{ edi_get('dx', 'code') }}                    as diagnosis_code
from flattened
