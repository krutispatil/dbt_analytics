with source as (

    select * from {{ source('olist', 'raw_orders') }}

),

renamed as (

    select
        order_id,
        customer_id,
        order_status,
        cast(order_purchase_timestamp as timestamp)      as ordered_at,
        cast(order_approved_at as timestamp)             as approved_at,
        cast(order_delivered_carrier_date as timestamp)  as shipped_at,
        cast(order_delivered_customer_date as timestamp) as delivered_at,
        cast(order_estimated_delivery_date as timestamp) as estimated_delivery_at,
        case
            when order_status = 'delivered'
                and cast(order_delivered_customer_date as timestamp)
                    <= cast(order_estimated_delivery_date as timestamp)
            then true
            else false
        end as is_delivered_on_time
    from source
    where order_id is not null

)

select * from renamed
