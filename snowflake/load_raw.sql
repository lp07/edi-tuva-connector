-- Load the parser output into raw VARIANT tables.
-- Run in a Snowsight worksheet as ACCOUNTADMIN, after snowflake/setup.sql.
use database edi;
use schema edi_raw;

create or replace table claims_837 (record variant);
create or replace table remit_835  (record variant);

-- Option A (recommended): stage + COPY.
-- 1. create a stage and file format that strips the outer JSON array
create file format if not exists json_array type = json strip_outer_array = true;
create stage if not exists edi_raw_stage file_format = json_array;
-- 2. upload sample_data/parsed/claims_837.json and remit_835.json to @edi_raw_stage
--    (snowsql:  put file://sample_data/parsed/claims_837.json @edi_raw_stage auto_compress=false overwrite=true;)
-- 3. load each top-level array element as one VARIANT row
copy into claims_837 (record)
    from (select $1 from @edi_raw_stage/claims_837.json (file_format => 'json_array'))
    on_error = 'abort_statement';
copy into remit_835 (record)
    from (select $1 from @edi_raw_stage/remit_835.json (file_format => 'json_array'))
    on_error = 'abort_statement';

-- Option B (no stage, paste the JSON): replace the placeholders with each file's
-- full contents between the $$ markers, then run.
-- insert into claims_837 (record)
-- select value from table(flatten(input => parse_json($$PASTE_CLAIMS_837_JSON$$)));
-- insert into remit_835 (record)
-- select value from table(flatten(input => parse_json($$PASTE_REMIT_835_JSON$$)));

-- sanity: expect 5 and 5
select 'claims_837' as t, count(*) as n from claims_837
union all
select 'remit_835', count(*) from remit_835;
