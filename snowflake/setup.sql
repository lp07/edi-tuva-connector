-- One-time Snowflake setup: database, schemas, warehouse.
-- Run in a Snowsight worksheet as ACCOUNTADMIN.
use role accountadmin;

create database if not exists edi;
create schema   if not exists edi.edi_raw;    -- holds the loaded JSON (VARIANT)
create schema   if not exists edi.edi_tuva;   -- where dbt builds the models

create warehouse if not exists compute_wh
    warehouse_size = xsmall
    auto_suspend   = 60
    auto_resume    = true;
