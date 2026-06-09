-- stg_837_claim  | grain: one row per 837P claim. Typed select only.
select
    {{ edi_get('', 'claim_id') }}                                as claim_id,
    {{ edi_get('', 'st_control_number') }}                       as transaction_control_number,
    {{ edi_get('', 'total_charge', 'decimal(18,2)') }}           as total_charge_amount,
    {{ edi_get('', 'place_of_service') }}                        as place_of_service_code,
    {{ edi_get('', 'facility_code_qualifier') }}                 as facility_code_qualifier,
    {{ edi_get('', 'claim_frequency_code') }}                    as claim_frequency_code,
    {{ edi_get('', 'billing_provider.name') }}                   as billing_provider_name,
    {{ edi_get('', 'billing_provider.npi') }}                    as billing_provider_npi,
    {{ edi_get('', 'payer.name') }}                              as payer_name,
    {{ edi_get('', 'payer.id') }}                                as payer_id,
    {{ edi_get('', 'subscriber.last_name') }}                    as subscriber_last_name,
    {{ edi_get('', 'subscriber.first_name') }}                   as subscriber_first_name,
    {{ edi_get('', 'subscriber.member_id') }}                    as member_id,
    {{ edi_get('', 'subscriber.id_qualifier') }}                 as member_id_qualifier,
    {{ edi_get('', 'subscriber.dob', 'date') }}                  as subscriber_dob,
    {{ edi_get('', 'subscriber.gender') }}                       as subscriber_gender,
    {{ edi_get('', 'subscriber.payer_responsibility') }}         as payer_responsibility_code,
    {{ edi_get('', 'subscriber.group_number') }}                 as subscriber_group_number,
    {{ edi_get('', 'subscriber.claim_filing_indicator') }}       as claim_filing_indicator_code,
    {{ edi_get('', 'rendering_provider_npi') }}                  as claim_rendering_provider_npi
from {{ source('edi_parsed', 'claims_837') }}
