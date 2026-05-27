with source as (

    select * from {{ source('edi_raw', 'reconciliation_report') }}

),

renamed as (

    select
        claim_id,
        patient_id                          as patient_id,
        patient_id                          as member_id,
        payer                               as payer_name,
        payer                               as payer_id,
        procedure_code                      as hcpcs_code,
        cast(date_of_service as date)       as claim_start_date,
        cast(date_of_service as date)       as claim_end_date,
        cast(date_of_service as date)       as service_start_date,
        cast(date_of_service as date)       as service_end_date,
        billed_amount                       as charge_amount,
        allowed_amount                      as allowed_amount,
        paid_amount                         as paid_amount,
        patient_responsibility              as coinsurance_amount,
        contractual_adjustment              as contractual_adjustment,
        status                              as claim_status_code,
        check_number                        as payer_claim_number,
        'professional'                      as claim_type,
        'edi_837_835_feed'                  as data_source_name

    from source

)

select * from renamed