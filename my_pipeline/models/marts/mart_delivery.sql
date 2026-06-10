with orders as (

    select * from {{ ref('int_orders_enriched') }}

),

final as (

    select
        -- dimensions
        date_trunc('month', ordered_at)         as order_month,
        customer_state,

        -- volume
        count(distinct order_id)                as total_orders,
        count(distinct case when order_status
            = 'delivered' then order_id end)    as delivered_orders,
        count(distinct case when order_status
            = 'canceled' then order_id end)     as canceled_orders,

        -- delivery speed
        round(avg(days_to_deliver), 1)          as avg_days_to_deliver,
        round(avg(estimated_delivery_days), 1)  as avg_estimated_days,
        round(avg(days_in_transit), 1)          as avg_days_in_transit,
        min(days_to_deliver)                    as fastest_delivery_days,
        max(days_to_deliver)                    as slowest_delivery_days,

        -- SLA performance
        sum(case when is_delivered_on_time
            then 1 else 0 end)                  as on_time_deliveries,
        coalesce(round(
            sum(case when is_delivered_on_time
                then 1 else 0 end) * 100.0
            / nullif(count(distinct case when order_status
                = 'delivered' then order_id end), 0)
        , 2), 0)                                as on_time_delivery_rate,

        -- late deliveries
        sum(case when order_status = 'delivered'
            and not is_delivered_on_time
            then 1 else 0 end)                  as late_deliveries,
        round(avg(case when order_status = 'delivered'
            and not is_delivered_on_time
            then days_to_deliver - estimated_delivery_days
        end), 1)                                as avg_days_late

    from orders
    where ordered_at is not null
    group by
        date_trunc('month', ordered_at),
        customer_state

)

select * from final
