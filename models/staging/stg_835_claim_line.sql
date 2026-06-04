-- stg_835_claim_line
-- Grain: one row per 835 service line (SVC loop).
-- Flattens the claim payment's own service_lines[] array. line_sequence is the
-- parser-assigned position within the claim and is the positional join key to
-- stg_837_claim_line. remark_codes stays a typed varchar list (empty in
-- synthetic data; populated by real remittances with LQ*HE segments).

with source as (

    select claim_id, service_lines
    from {{ source('edi_parsed', 'remit_835') }}

),

flattened as (

    select
        claim_id,
        unnest(service_lines) as line
    from source

)

select
    cast(claim_id as varchar)                          as claim_id,
    try_cast(line.line_sequence as integer)                as line_sequence,
    cast(line.procedure_code as varchar)               as procedure_code,
    cast(line.modifiers as varchar[])                  as modifiers,
    try_cast(line.line_charge as decimal(18, 2))           as line_charge_amount,
    try_cast(line.line_paid as decimal(18, 2))             as line_paid_amount,
    try_cast(line.units_paid as decimal(12, 3))            as paid_unit_count,
    try_strptime(line.service_date, '%Y%m%d')::date    as service_date,
    cast(line.line_control_number as varchar)          as line_control_number,
    cast(line.remark_codes as varchar[])               as remark_codes
from flattened
