-- stg_837_claim
-- Grain: one row per 837P claim.
-- Typed select only. Flattens the claim-level struct fields and casts. No joins,
-- no business logic, no Tuva names (mapping happens in intermediate).

with source as (

    select * from {{ source('edi_parsed', 'claims_837') }}

)

select
    cast(claim_id as varchar)                              as claim_id,
    cast(st_control_number as varchar)                     as transaction_control_number,
    try_cast(total_charge as decimal(18, 2))                   as total_charge_amount,
    cast(place_of_service as varchar)                      as place_of_service_code,
    cast(facility_code_qualifier as varchar)               as facility_code_qualifier,
    cast(claim_frequency_code as varchar)                  as claim_frequency_code,
    cast(billing_provider.name as varchar)                 as billing_provider_name,
    cast(billing_provider.npi as varchar)                  as billing_provider_npi,
    cast(payer.name as varchar)                            as payer_name,
    cast(payer.id as varchar)                              as payer_id,
    cast(subscriber.last_name as varchar)                  as subscriber_last_name,
    cast(subscriber.first_name as varchar)                 as subscriber_first_name,
    cast(subscriber.member_id as varchar)                  as member_id,
    cast(subscriber.id_qualifier as varchar)               as member_id_qualifier,
    try_strptime(subscriber.dob, '%Y%m%d')::date           as subscriber_dob,
    cast(subscriber.gender as varchar)                     as subscriber_gender,
    cast(subscriber.payer_responsibility as varchar)       as payer_responsibility_code,
    cast(subscriber.group_number as varchar)               as subscriber_group_number,
    cast(subscriber.claim_filing_indicator as varchar)     as claim_filing_indicator_code,
    cast(rendering_provider_npi as varchar)                as claim_rendering_provider_npi
from source
