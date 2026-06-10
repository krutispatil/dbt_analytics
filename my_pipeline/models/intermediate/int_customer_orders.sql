with orders as (

    select * from {{ ref('int_orders_enriched') }}

),

customer_metrics as (

    select
        customer_unique_id,

        -- order counts
        count(distinct order_id)                                    as total_orders,
        count(distinct case
            when order_status = 'delivered' then order_id
        end)                                                        as delivered_orders,

        -- revenue metrics
        sum(total_order_revenue)                                    as lifetime_revenue,
        avg(total_order_revenue)                                    as avg_order_value,
        min(total_order_revenue)                                    as min_order_value,
        max(total_order_revenue)                                    as max_order_value,

        -- timing
        min(ordered_at)                                             as first_order_at,
        max(ordered_at)                                             as last_order_at,
        datediff('day', min(ordered_at), max(ordered_at))          as customer_lifespan_days,

        -- delivery experience
        avg(days_to_deliver)                                        as avg_days_to_deliver,
        sum(case when is_delivered_on_time then 1 else 0 end)      as on_time_deliveries,

        -- customer segmentation
        case
            when count(distinct order_id) = 1 then 'one_time'
            when count(distinct order_id) between 2 and 3 then 'repeat'
            else 'loyal'
        end                                                         as customer_segment

    from orders
    where customer_unique_id is not null
    group by customer_unique_id

)

select * from customer_metrics
