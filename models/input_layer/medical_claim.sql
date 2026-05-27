with claims as (

    select * from {{ ref('stg_837_claims') }}

),

remittance as (

    select * from {{ ref('stg_835_remittance') }}

),

joined as (

    select
        c.claim_id,
        null                                as claim_line_number,
        c.claim_type,
        c.patient_id,
        c.member_id,
        c.payer_id,
        c.payer_name,
        null                                as plan_name,
        c.claim_start_date,
        c.claim_end_date,
        c.service_start_date,
        c.service_end_date,
        null                                as place_of_service_code,
        null                                as bill_type_code,
        null                                as revenue_center_code,
        c.hcpcs_code,
        null                                as hcpcs_modifier_1,
        null                                as hcpcs_modifier_2,
        null                                as hcpcs_modifier_3,
        null                                as hcpcs_modifier_4,
        null                                as diagnosis_code_1,
        null                                as diagnosis_code_2,
        null                                as diagnosis_code_3,
        null                                as diagnosis_code_type,
        null                                as billing_npi,
        null                                as rendering_npi,
        null                                as facility_npi,
        null                                as referring_npi,
        null                                as admit_source_code,
        null                                as admit_type_code,
        null                                as discharge_disposition_code,
        c.charge_amount,
        r.paid_amount,
        r.allowed_amount,
        r.patient_responsibility            as coinsurance_amount,
        null                                as copayment_amount,
        null                                as deductible_amount,
        r.paid_amount                       as total_cost_amount,
        r.claim_status_code,
        r.payer_claim_number,
        c.data_source_name

    from claims c
    left join remittance r
        on c.claim_id = r.claim_id

)

select * from joined