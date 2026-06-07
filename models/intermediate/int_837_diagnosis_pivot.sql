-- int_837_diagnosis_pivot
-- Grain: one row per claim.
-- Pivots the long claim-diagnosis rows into Tuva's wide diagnosis_code_1..25,
-- ordered by the HI ordinal (diagnosis_sequence). Also derives
-- diagnosis_code_type from the HI qualifier: ABK/ABF are ICD-10-CM, BK/BF are
-- ICD-9-CM. Tuva carries diagnoses at claim level repeated per line, so this
-- pivot is joined onto every line in int_medical_claim.

with dx as (

    select
        claim_id,
        diagnosis_sequence,
        diagnosis_qualifier_code,
        diagnosis_code
    from {{ ref('stg_837_diagnosis') }}

)

select
    claim_id,
    max(
        case
            when diagnosis_qualifier_code in ('ABK', 'ABF') then 'icd-10-cm'
            when diagnosis_qualifier_code in ('BK', 'BF') then 'icd-9-cm'
        end
    ) as diagnosis_code_type
    {% for i in range(1, 26) %}
    , max(case when diagnosis_sequence = {{ i }} then diagnosis_code end) as diagnosis_code_{{ i }}
    {% endfor %}
from dx
group by claim_id
