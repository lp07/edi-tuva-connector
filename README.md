# EDI 837/835 Tuva Connector

A dbt connector that maps parsed EDI X12 837 and 835 data into the Tuva health data framework input layer.

## What this does

Healthcare organizations that receive raw EDI claim files have no direct path into Tuva today. This connector bridges that gap. It takes parsed 837 professional and institutional claims alongside 835 remittance data and transforms them into Tuva's standardized medical_claim input structure.

The result is a complete claims pipeline: raw EDI files flow through a Python parser into Snowflake staging tables, and this connector maps that staging data into Tuva's input layer so the full suite of Tuva data marts can run on top.

## Architecture

Raw EDI 837/835 files, Python parser, Snowflake staging tables, this connector, Tuva input layer, Tuva data marts.

## Source data

This connector expects parsed EDI data in Snowflake staging tables. The upstream Python parser that produces this staging data is available at: https://github.com/lp07/835-837-Remittance-Reconciliation-Pipeline

## Models

staging/
  stg_837_claims.sql maps parsed 837 professional claims to Tuva medical_claim fields
  stg_835_remittance.sql maps parsed 835 remittance data to Tuva financial fields

input_layer/
  medical_claim.sql final Tuva-compliant medical_claim input table

## Requirements

dbt-core 1.6 or higher
dbt-duckdb for local development or dbt-snowflake for production
Tuva package installed via dbt deps

## Getting started

Clone this repo, install dependencies, and run:

dbt deps
dbt run

## Status

Active development. First stable release targeting Tuva v0.17.x input layer specification.