with seller_performance as (

    select * from {{ ref('int_seller_performance') }}

),

final as (

    select
        seller_id,
        seller_city,
        seller_state,

        -- volume
        total_orders,
        total_items_sold,
        unique_products,

        -- revenue
        round(total_revenue, 2)                 as total_revenue,
        round(avg_item_price, 2)                as avg_item_price,
        round(total_freight_collected, 2)       as total_freight_collected,

        -- delivery
        round(avg_days_to_deliver, 1)           as avg_days_to_deliver,
        delivered_orders,
        on_time_deliveries,
        round(
            on_time_deliveries * 100.0 / nullif(delivered_orders, 0), 2
        )                                       as on_time_rate,

        -- reviews
        round(avg_review_score, 2)              as avg_review_score,
        total_reviews,
        positive_reviews,
        negative_reviews,
        round(
            positive_reviews * 100.0 / nullif(total_reviews, 0), 2
        )                                       as positive_review_rate,

        -- seller health score (composite metric)
        round(
            (coalesce(avg_review_score, 0) / 5.0 * 40)
            + (coalesce(on_time_deliveries * 100.0 / nullif(delivered_orders, 0), 0) / 100.0 * 40)
            + (least(total_orders, 100) / 100.0 * 20)
        , 2)                                    as seller_health_score

    from seller_performance

)

select * from final
