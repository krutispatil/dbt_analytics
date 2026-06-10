with order_items as (

    select * from {{ ref('stg_order_items') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

reviews as (

    select * from {{ ref('stg_reviews') }}

),

sellers as (

    select * from {{ ref('stg_sellers') }}

),

products as (

    select * from {{ ref('stg_products') }}

),

translations as (

    select * from {{ ref('stg_product_category_translations') }}

),

seller_metrics as (

    select
        oi.seller_id,
        s.city                              as seller_city,
        s.state                             as seller_state,

        -- volume metrics
        count(distinct oi.order_id)         as total_orders,
        count(oi.order_item_id)             as total_items_sold,
        count(distinct oi.product_id)       as unique_products,

        -- revenue metrics
        sum(oi.item_price)                  as total_revenue,
        avg(oi.item_price)                  as avg_item_price,
        sum(oi.freight_cost)                as total_freight_collected,

        -- delivery metrics
        avg(case
            when o.order_status = 'delivered'
            then datediff('day', o.ordered_at, o.delivered_at)
        end)                                as avg_days_to_deliver,
        sum(case
            when o.is_delivered_on_time then 1 else 0
        end)                                as on_time_deliveries,
        count(distinct case
            when o.order_status = 'delivered' then o.order_id
        end)                                as delivered_orders,

        -- review metrics
        avg(r.review_score)                 as avg_review_score,
        count(r.review_id)                  as total_reviews,
        sum(case
            when r.review_score >= 4 then 1 else 0
        end)                                as positive_reviews,
        sum(case
            when r.review_score <= 2 then 1 else 0
        end)                                as negative_reviews

    from order_items oi
    left join sellers s
        on oi.seller_id = s.seller_id
    left join orders o
        on oi.order_id = o.order_id
    left join reviews r
        on oi.order_id = r.order_id

    group by oi.seller_id, s.city, s.state

)

select * from seller_metrics
