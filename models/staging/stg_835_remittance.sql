with source as (

    select * from {{ source('edi_raw', 'reconciliation_report') }}

),

remittance as (

    select
        claim_id,
        payer                               as payer_id,
        payer                               as payer_name,
        check_number                        as payer_claim_number,
        cast(remittance_date as date)       as remittance_date,
        days_to_payment,
        paid_amount,
        allowed_amount,
        patient_responsibility,
        contractual_adjustment,
        carc_codes,
        rarc_codes,
        primary_carc,
        contracted_rate,
        variance_amount,
        variance_pct,
        recovery_amount,
        status                              as claim_status_code,
        denial_category

    from source

)

select * from remittance