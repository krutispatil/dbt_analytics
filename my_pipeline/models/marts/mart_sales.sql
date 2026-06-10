with orders as (

    select * from {{ ref('int_orders_enriched') }}

),

products as (

    select * from {{ ref('stg_products') }}

),

translations as (

    select * from {{ ref('stg_product_category_translations') }}

),

order_items as (

    select * from {{ ref('stg_order_items') }}

),

items_with_category as (

    select
        oi.order_id,
        oi.product_id,
        oi.seller_id,
        oi.item_price,
        oi.freight_cost,
        oi.total_item_revenue,
        coalesce(t.category_name_english, p.category_name, 'unknown') as category_name_english
    from order_items oi
    left join products p
        on oi.product_id = p.product_id
    left join translations t
        on p.category_name = t.category_name

),

final as (

    select
        -- date dimensions
        date_trunc('month', o.ordered_at)       as order_month,
        date_trunc('week', o.ordered_at)        as order_week,
        cast(o.ordered_at as date)              as order_date,

        -- location
        o.customer_state,
        o.customer_city,

        -- category
        i.category_name_english,

        -- order metrics
        count(distinct o.order_id)              as total_orders,
        count(distinct o.customer_unique_id)    as unique_customers,
        sum(o.total_order_revenue)              as total_revenue,
        avg(o.total_order_revenue)              as avg_order_value,
        sum(o.total_items)                      as total_items_sold,
        sum(o.total_freight_cost)               as total_freight,

        -- delivery metrics
        avg(o.days_to_deliver)                  as avg_days_to_deliver,
        sum(case when o.is_delivered_on_time
            then 1 else 0 end)                  as on_time_orders,
        count(distinct case when o.order_status
            = 'canceled' then o.order_id end)   as canceled_orders

    from orders o
    left join items_with_category i
        on o.order_id = i.order_id

    group by
        date_trunc('month', o.ordered_at),
        date_trunc('week', o.ordered_at),
        cast(o.ordered_at as date),
        o.customer_state,
        o.customer_city,
        i.category_name_english

)

select * from final
