{{ config(enabled = var('claims_enabled', false) | as_bool) }}
-- PLACEHOLDER. the_tuva_project's input_layer__eligibility is
-- `select * from ref('eligibility')`, so this node must exist for the package to
-- compile when claims_enabled is true. It returns zero rows so the medical_claim
-- DQI tests can be run in isolation. Replace with a real eligibility mapping (or
-- remove, with claims_enabled handling) before using enrollment-dependent marts.
select
    cast(null as varchar) as person_id,
    cast(null as varchar) as member_id,
    cast(null as varchar) as payer,
    cast(null as varchar) as plan,
    cast(null as date)    as enrollment_start_date,
    cast(null as date)    as enrollment_end_date,
    cast(null as varchar) as data_source
where 1 = 0
