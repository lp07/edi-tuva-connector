# EDI 837/835 Tuva Connector

A dbt connector that maps parsed EDI X12 837 and 835 data into the Tuva health data framework input layer.

## What this does

Healthcare organizations that receive raw EDI claim files have no direct path into Tuva today. This connector bridges that gap. It takes parsed 837 professional claims alongside 835 remittance data and transforms them into Tuva's standardized medical_claim input structure.

The pipeline runs as one cohesive system. A Python ingestion script reads parsed EDI output and loads it directly into DuckDB. The dbt connector then builds staging models and materializes the final Tuva-compliant medical_claim table on top.

## Architecture

Raw EDI 837/835 files, Python parser, DuckDB staging tables, this connector, Tuva input layer, Tuva data marts.

## How to run

Step 1. Clone this repo and activate your Python environment.

Step 2. Install dependencies:

    pip install dbt-duckdb pandas

Step 3. Load source data into DuckDB:

    python ingest.py

Step 4. Build the connector models:

    dbt run

Step 5. Run data quality tests:

    dbt test

By default ingest.py reads from seeds/reconciliation_report.csv. To point it at your own parsed EDI output set the EDI_SOURCE_PATH environment variable:

    EDI_SOURCE_PATH=/path/to/your/parsed_claims.csv python ingest.py

## Models

staging/stg_837_claims.sql maps parsed 837 professional claim fields to Tuva medical_claim input structure including claim identifiers, dates, procedure codes, and charge amounts.

staging/stg_835_remittance.sql maps parsed 835 remittance fields including paid amounts, allowed amounts, adjustment codes, and claim status.

input_layer/medical_claim.sql joins both staging models into the final Tuva-compliant medical_claim table.

## Current field coverage

The following Tuva medical_claim fields are populated from the current parser output:

claim_id, patient_id, member_id, payer_id, payer_name, claim_type, claim_start_date, claim_end_date, service_start_date, service_end_date, hcpcs_code, charge_amount, allowed_amount, paid_amount, coinsurance_amount, claim_status_code, payer_claim_number, data_source_name.

The following fields require a deeper segment-level EDI parser and are currently null:

diagnosis_code_1 through diagnosis_code_25, billing_npi, rendering_npi, facility_npi, hcpcs_modifier_1 through hcpcs_modifier_4, claim_line_number, place_of_service_code, bill_type_code, revenue_center_code, admit_source_code, admit_type_code, discharge_disposition_code.

Expanding parser coverage to capture these fields is the next development priority.

## Data quality tests

8 tests covering not_null constraints on required fields and accepted_values validation on claim_type. All passing against the sample dataset of 1,200 claims.

## Requirements

dbt-core 1.6 or higher, dbt-duckdb for local development or dbt-snowflake for production, pandas for the ingestion script.

## Status

Active development. Current version maps core financial and claim identity fields. Next milestone is full segment-level EDI parsing to populate clinical fields including diagnosis codes and provider NPIs.