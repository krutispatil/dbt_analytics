with orders as (

    select * from {{ ref('stg_orders') }}

),

customers as (

    select * from {{ ref('stg_customers') }}

),

payments as (

    select
        order_id,
        sum(payment_value)                    as total_payment_value,
        count(distinct payment_type)          as payment_methods_used,
        max(payment_installments)             as max_installments,
        listagg(distinct payment_type, ', ')  as payment_types
    from {{ ref('stg_payments') }}
    group by order_id

),

order_items as (

    select
        order_id,
        count(order_item_id)        as total_items,
        sum(item_price)             as total_items_price,
        sum(freight_cost)           as total_freight_cost,
        sum(total_item_revenue)     as total_order_revenue,
        count(distinct seller_id)   as unique_sellers
    from {{ ref('stg_order_items') }}
    group by order_id

),

final as (

    select
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        c.city                                                          as customer_city,
        c.state                                                         as customer_state,
        o.order_status,
        o.ordered_at,
        o.approved_at,
        o.shipped_at,
        o.delivered_at,
        o.estimated_delivery_at,
        o.is_delivered_on_time,
        datediff('day', o.ordered_at, o.delivered_at)                  as days_to_deliver,
        datediff('day', o.ordered_at, o.estimated_delivery_at)         as estimated_delivery_days,
        datediff('day', o.shipped_at, o.delivered_at)                  as days_in_transit,
        coalesce(p.total_payment_value, 0)                             as total_payment_value,
        coalesce(p.payment_methods_used, 0)                            as payment_methods_used,
        coalesce(p.max_installments, 0)                                as max_installments,
        p.payment_types,
        coalesce(oi.total_items, 0)                                    as total_items,
        coalesce(oi.total_items_price, 0)                              as total_items_price,
        coalesce(oi.total_freight_cost, 0)                             as total_freight_cost,
        coalesce(oi.total_order_revenue, 0)                            as total_order_revenue,
        coalesce(oi.unique_sellers, 0)                                 as unique_sellers

    from orders o
    left join customers c
        on o.customer_id = c.customer_id
    left join payments p
        on o.order_id = p.order_id
    left join order_items oi
        on o.order_id = oi.order_id

)

select * from final
