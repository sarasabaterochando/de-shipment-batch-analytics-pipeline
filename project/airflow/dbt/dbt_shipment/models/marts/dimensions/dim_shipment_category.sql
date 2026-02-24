{{ config(
    materialized='table'
) }}

with unique_categories as (
    select distinct
       shipment_category
    from {{ ref('stg_batch_shipment') }}
    where shipment_category is not null
),

add_surrogate_key as (
    select
        {{ dbt_utils.generate_surrogate_key(['shipment_category']) }} as id_shipment_category,
        shipment_category
    from unique_categories
)

select
    id_shipment_category,
    shipment_category
from add_surrogate_key
order by shipment_category