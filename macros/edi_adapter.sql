{#
  Adapter-aware ingestion macros for the edi-tuva-connector.
  ALL DuckDB vs Snowflake branching lives here. Model bodies only call these
  macros; they contain no {% if target.type %} blocks.

  DuckDB: parser JSON read via read_json_auto (sources.yml external_location),
          giving typed STRUCT/LIST columns. Field access is dotted; arrays are
          LIST; dates parse with strptime; numerics with try_cast.
  Snowflake: parser JSON loaded into a raw table with a single VARIANT column
          named `record`. Field access is colon-path; arrays flatten with
          LATERAL FLATTEN; dates with try_to_date; numerics with try_to_decimal.
#}

{# ---- edi_get: typed field extraction ------------------------------------ #}
{# obj: '' for a top-level field, or the alias of a flattened element (e.g. 'line').
   path: dotted path within the object (e.g. 'billing_provider.npi').
   type: 'varchar' | 'integer' | 'decimal(p,s)' | 'date' | 'array'           #}
{% macro edi_get(obj, path, type='varchar') %}
{%- if target.type == 'duckdb' -%}
    {%- set base = path if obj == '' else obj ~ '.' ~ path -%}
    {%- if type == 'date' -%}
        try_strptime({{ base }}, '%Y%m%d')::date
    {%- elif type == 'array' -%}
        cast({{ base }} as varchar[])
    {%- elif type.startswith('decimal') or type == 'integer' -%}
        try_cast({{ base }} as {{ type }})
    {%- else -%}
        cast({{ base }} as {{ type }})
    {%- endif -%}
{%- elif target.type == 'snowflake' -%}
    {%- set root = 'record' if obj == '' else obj -%}
    {%- set jpath = root ~ ':' ~ (path | replace('.', ':')) -%}
    {%- if type == 'date' -%}
        try_to_date({{ jpath }}::varchar, 'YYYYMMDD')
    {%- elif type == 'array' -%}
        {{ jpath }}::array
    {%- elif type.startswith('decimal') -%}
        {%- set ps = type.split('(')[1].rstrip(')') -%}
        try_to_decimal({{ jpath }}::varchar, {{ ps }})
    {%- elif type == 'integer' -%}
        try_cast({{ jpath }}::varchar as integer)
    {%- else -%}
        {{ jpath }}::varchar
    {%- endif -%}
{%- endif -%}
{% endmacro %}


{# ---- edi_flatten: one row per array element ------------------------------ #}
{# Source-level:  edi_flatten('service_lines', 'line', source_name='claims_837')
   Nested level:  edi_flatten('line_adjustments', 'adj', from_rel='lines', parent='line', element_struct='...')
   element_struct (DuckDB only) pins the array element type so empty arrays do
   not break type inference; ignored on Snowflake.                            #}
{% macro edi_flatten(array_path, alias, source_name=none, from_rel=none, parent='', element_struct=none) %}
{%- if target.type == 'duckdb' -%}
    {%- set rel = source('edi_parsed', source_name) if source_name else from_rel -%}
    {%- set accessor = array_path if source_name else parent ~ '.' ~ array_path -%}
    {%- if element_struct -%}
        {%- set accessor = 'cast(' ~ accessor ~ ' as struct(' ~ element_struct ~ ')[])' -%}
    {%- endif -%}
    select *, unnest({{ accessor }}) as {{ alias }}
    from {{ rel }}
{%- elif target.type == 'snowflake' -%}
    {%- if source_name -%}
        {%- set rel = source('edi_parsed', source_name) -%}
        {%- set input = 'src.record:' ~ array_path -%}
        select src.*, f.value as {{ alias }}
        from {{ rel }} as src,
             lateral flatten(input => {{ input }}) as f
    {%- else -%}
        {%- set input = parent ~ ':' ~ array_path -%}
        select base.*, f.value as {{ alias }}
        from {{ from_rel }} as base,
             lateral flatten(input => {{ input }}) as f
    {%- endif -%}
{%- endif -%}
{% endmacro %}


{# ---- edi_array_element: nth element of an array column ------------------- #}
{# n is 1-based (DuckDB convention); the macro translates to 0-based on Snowflake. #}
{% macro edi_array_element(arr, n, type='varchar') %}
{%- if target.type == 'duckdb' -%}
    {{ arr }}[{{ n }}]
{%- elif target.type == 'snowflake' -%}
    {{ arr }}[{{ n - 1 }}]::{{ type }}
{%- endif -%}
{% endmacro %}
