with dedup_query as(
select *,
row_number() over (partition by id order by updatedDate desc) as deduplication_id

 from {{ source('source', 'items') }}
 --where deduplication_id = 1
)
select id, name , category, updatedDate
from dedup_query
where deduplication_id = 1
