-- in bronze just pull the data from source layer
--select * from dbt_practice_dev.source.fact_sales -- using dynamic
{{config(materialized='view')}}
select * from {{ source('source', 'fact_sales') }}