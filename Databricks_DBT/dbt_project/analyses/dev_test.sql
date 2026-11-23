-- this file is for developer testing purpose only. It is not part of the dbt project and will be ignored by dbt.
select * from {{ ref('lookup') }}