-- stg_835_claim
-- Grain: one row per 835 claim payment (CLP loop).
-- Typed select only. No joins, no logic. claim_status_code and the CARC/CAS
-- detail are carried raw; denial and reversal classification is intermediate's.

with source as (

    select * from {{ source('edi_parsed', 'remit_835') }}

)

select
    cast(claim_id as varchar)                          as claim_id,
    cast(st_control_number as varchar)                 as transaction_control_number,
    cast(trace_number as varchar)                      as payment_trace_number,
    cast(payer_name as varchar)                        as payer_name,
    cast(payee_name as varchar)                        as payee_name,
    try_cast(payment_total as decimal(18, 2))              as payment_total_amount,
    cast(claim_status_code as varchar)                 as claim_status_code,
    try_cast(claim_charge as decimal(18, 2))               as claim_charge_amount,
    try_cast(claim_paid as decimal(18, 2))                 as claim_paid_amount,
    try_cast(patient_responsibility as decimal(18, 2))     as patient_responsibility_amount,
    cast(claim_filing_indicator as varchar)            as claim_filing_indicator_code,
    cast(payer_claim_control_number as varchar)        as payer_claim_control_number
from source
