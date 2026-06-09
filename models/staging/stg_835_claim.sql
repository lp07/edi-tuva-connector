-- stg_835_claim | grain: one row per 835 claim payment. Typed select only.
select
    {{ edi_get('', 'claim_id') }}                              as claim_id,
    {{ edi_get('', 'st_control_number') }}                     as transaction_control_number,
    {{ edi_get('', 'trace_number') }}                          as payment_trace_number,
    {{ edi_get('', 'payer_name') }}                            as payer_name,
    {{ edi_get('', 'payee_name') }}                            as payee_name,
    {{ edi_get('', 'payment_total', 'decimal(18,2)') }}        as payment_total_amount,
    {{ edi_get('', 'claim_status_code') }}                     as claim_status_code,
    {{ edi_get('', 'claim_charge', 'decimal(18,2)') }}         as claim_charge_amount,
    {{ edi_get('', 'claim_paid', 'decimal(18,2)') }}           as claim_paid_amount,
    {{ edi_get('', 'patient_responsibility', 'decimal(18,2)') }} as patient_responsibility_amount,
    {{ edi_get('', 'claim_filing_indicator') }}                as claim_filing_indicator_code,
    {{ edi_get('', 'payer_claim_control_number') }}            as payer_claim_control_number
from {{ source('edi_parsed', 'remit_835') }}
