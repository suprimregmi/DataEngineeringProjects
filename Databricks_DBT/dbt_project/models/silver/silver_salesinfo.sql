with bronze_sales as (
    select sales_id,
      product_id,
      customer_sk,
      {{multiply('unit_price', 'quantity')}} as gross_amount_calculated,
      date_sk,
      customer_id,
      gross_amount,
      payment_method from {{ ref('bronze_sales') }}
),
products as (
    select product_sk, category
      from {{ ref('bronze_product') }}
),
customer AS(

    select customer_sk, gender
      from {{ ref('bronze_customer') }}
)

select * from bronze_sales join products p on j.product_id = p.product_sk
join customer c on j.customer_sk = c.customer_sk


