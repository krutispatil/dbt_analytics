with customer_orders as (

    select * from {{ ref('int_customer_orders') }}

),

final as (

    select
        customer_unique_id,
        customer_segment,

        -- order behaviour
        total_orders,
        delivered_orders,
        round(
            delivered_orders * 100.0 / nullif(total_orders, 0), 2
        )                                       as delivery_success_rate,

        -- revenue
        round(lifetime_revenue, 2)              as lifetime_revenue,
        round(avg_order_value, 2)               as avg_order_value,
        round(min_order_value, 2)               as min_order_value,
        round(max_order_value, 2)               as max_order_value,

        -- timing
        first_order_at,
        last_order_at,
        customer_lifespan_days,

        -- delivery experience
        round(avg_days_to_deliver, 1)           as avg_days_to_deliver,
        on_time_deliveries,
        round(
            on_time_deliveries * 100.0 / nullif(delivered_orders, 0), 2
        )                                       as on_time_rate

    from customer_orders

)

select * from final
