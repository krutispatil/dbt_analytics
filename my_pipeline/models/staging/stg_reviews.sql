with source as (

    select * from {{ source('olist', 'raw_reviews') }}

),

renamed as (

    select
        review_id,
        order_id,
        review_score,
        cast(review_creation_date as timestamp)    as review_created_at,
        cast(review_answer_timestamp as timestamp) as review_answered_at
    from source
    where review_id is not null
      and order_id is not null

),

deduped as (

    select *,
        row_number() over (
            partition by review_id
            order by review_created_at desc
        ) as row_num
    from renamed

)

select
    review_id,
    order_id,
    review_score,
    review_created_at,
    review_answered_at
from deduped
where row_num = 1
