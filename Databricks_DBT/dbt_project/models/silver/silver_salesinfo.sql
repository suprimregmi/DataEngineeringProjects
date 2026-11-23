with bronze_sales as (
    select
        sales_id,
        product_sk,
        customer_sk,
        {{ multiply('unit_price', 'quantity') }} as gross_amount_calculated,
        date_sk,
        gross_amount,
        payment_method
    from {{ ref('bronze_sales') }}
),
products as (
    select product_sk, category
    from {{ ref('bronze_product') }}
),
customer as (
    select customer_sk, gender
    from {{ ref('bronze_customer') }}
),
joined_cte as (
    select
        j.sales_id,
        j.product_sk,
        j.customer_sk,
        j.gross_amount_calculated,
        j.date_sk,
        j.gross_amount,
        j.payment_method,
        p.category,
        c.gender
    from bronze_sales j
    join products p on j.product_sk = p.product_sk
    join customer c on j.customer_sk = c.customer_sk
)
select
    category,
    gender,
    sum(gross_amount_calculated) as total_sales
from joined_cte
group by category, gender