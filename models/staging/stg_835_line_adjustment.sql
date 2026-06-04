-- stg_835_line_adjustment
-- Grain: one row per line-level CAS adjustment triplet (group_code, reason_code,
-- amount). Two-level flatten: service_lines[] then line_adjustments[]. The
-- adjustment list type is pinned with an explicit struct cast so the model is
-- robust even on claims/lines where the list is empty.

with source as (

    select claim_id, service_lines
    from {{ source('edi_parsed', 'remit_835') }}

),

lines as (

    select
        claim_id,
        unnest(service_lines) as line
    from source

),

adjustments as (

    select
        claim_id,
        line.line_sequence as line_sequence,
        unnest(
            cast(line.line_adjustments as
                struct(group_code varchar, reason_code varchar,
                       amount varchar, quantity varchar)[])
        ) as adj
    from lines

)

select
    cast(claim_id as varchar)            as claim_id,
    try_cast(line_sequence as integer)       as line_sequence,
    cast(adj.group_code as varchar)      as adjustment_group_code,
    cast(adj.reason_code as varchar)     as adjustment_reason_code,
    try_cast(adj.amount as decimal(18, 2))   as adjustment_amount,
    try_cast(adj.quantity as decimal(12, 3)) as adjustment_quantity
from adjustments
