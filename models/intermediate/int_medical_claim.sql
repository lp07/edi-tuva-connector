-- int_medical_claim | grain: one row per final-adjudicated 837P claim line.
-- Cross-source positional join (claim_id + line_sequence), header dates,
-- person_id from member_id, allowed_amount, denial/reversal handling. The only
-- adapter-specific piece is array element access, via the edi_array_element macro.
with line_837 as (
    select * from {{ ref('stg_837_claim_line') }}
),
claim_837 as (
    select * from {{ ref('stg_837_claim') }}
),
line_835 as (
    select * from {{ ref('stg_835_claim_line') }}
),
claim_835 as (
    select * from {{ ref('stg_835_claim') }}
),
financials as (
    select * from {{ ref('int_835_line_financials') }}
),
diagnoses as (
    select * from {{ ref('int_837_diagnosis_pivot') }}
),
joined as (
    select
        l8.claim_id,
        l8.line_sequence                                       as claim_line_number,
        'professional'                                         as claim_type,
        nullif(c8.member_id, '')                               as person_id,
        nullif(c8.member_id, '')                               as member_id,
        nullif(c8.payer_name, '')                              as payer,
        min(l8.service_date) over (partition by l8.claim_id)   as claim_start_date,
        max(l8.service_date) over (partition by l8.claim_id)   as claim_end_date,
        l8.service_date                                        as claim_line_start_date,
        l8.service_date                                        as claim_line_end_date,
        nullif(c8.place_of_service_code, '')                   as place_of_service_code,
        l8.unit_count                                          as service_unit_quantity,
        nullif(l8.procedure_code, '')                          as hcpcs_code,
        {{ edi_array_element('l8.modifiers', 1) }}             as hcpcs_modifier_1,
        {{ edi_array_element('l8.modifiers', 2) }}             as hcpcs_modifier_2,
        {{ edi_array_element('l8.modifiers', 3) }}             as hcpcs_modifier_3,
        {{ edi_array_element('l8.modifiers', 4) }}             as hcpcs_modifier_4,
        coalesce(nullif(l8.line_rendering_provider_npi, ''),
                 nullif(c8.claim_rendering_provider_npi, ''))  as rendering_npi,
        nullif(c8.billing_provider_npi, '')                    as billing_npi,
        l5.line_paid_amount                                    as paid_amount,
        (
            coalesce(l5.line_paid_amount, 0)
            + coalesce(fin.deductible_amount, 0)
            + coalesce(fin.coinsurance_amount, 0)
            + coalesce(fin.copayment_amount, 0)
        )                                                      as allowed_amount,
        l8.line_charge_amount                                  as charge_amount,
        fin.coinsurance_amount,
        fin.copayment_amount,
        fin.deductible_amount,
        dx.diagnosis_code_type
        {% for i in range(1, 26) %}
        , dx.diagnosis_code_{{ i }}
        {% endfor %}
        , cs.claim_status_code
    from line_837 l8
    inner join claim_837 c8
        on l8.claim_id = c8.claim_id
    left join line_835 l5
        on l8.claim_id = l5.claim_id
        and l8.line_sequence = l5.line_sequence
    left join claim_835 cs
        on l8.claim_id = cs.claim_id
    left join financials fin
        on l8.claim_id = fin.claim_id
        and l8.line_sequence = fin.line_sequence
    left join diagnoses dx
        on l8.claim_id = dx.claim_id
)
select *
from joined
where coalesce(claim_status_code, '') not in ('22')
