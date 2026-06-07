{{ config(enabled = var('claims_enabled', false) | as_bool) }}
-- PLACEHOLDER. the_tuva_project's input_layer__pharmacy_claim is
-- `select * from ref('pharmacy_claim')`, so this node must exist for the package
-- to compile when claims_enabled is true. Returns zero rows. Replace with a real
-- pharmacy mapping or remove before using pharmacy marts.
select
    cast(null as varchar) as claim_id,
    cast(null as integer) as claim_line_number,
    cast(null as varchar) as person_id,
    cast(null as varchar) as member_id,
    cast(null as date)    as dispensing_date,
    cast(null as varchar) as ndc_code,
    cast(null as varchar) as data_source
where 1 = 0
