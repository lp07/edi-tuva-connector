-- stg_835_claim_adjustment
-- Grain: one row per claim-level CAS adjustment triplet.
-- Empty in the current synthetic data, modeled now because real remittances
-- carry claim-level adjustments. The list type is pinned with an explicit struct
-- cast so the model compiles and returns zero rows rather than failing type
-- inference when every claim_level_adjustments array is empty.

with source as (

    select claim_id, claim_level_adjustments
    from {{ source('edi_parsed', 'remit_835') }}

),

adjustments as (

    select
        claim_id,
        unnest(
            cast(claim_level_adjustments as
                struct(group_code varchar, reason_code varchar,
                       amount varchar, quantity varchar)[])
        ) as adj
    from source

)

select
    cast(claim_id as varchar)            as claim_id,
    cast(adj.group_code as varchar)      as adjustment_group_code,
    cast(adj.reason_code as varchar)     as adjustment_reason_code,
    try_cast(adj.amount as decimal(18, 2))   as adjustment_amount,
    try_cast(adj.quantity as decimal(12, 3)) as adjustment_quantity
from adjustments
