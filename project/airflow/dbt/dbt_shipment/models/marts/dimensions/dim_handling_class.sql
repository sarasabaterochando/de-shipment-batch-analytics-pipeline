{{ config(
    materialized='table'
) }}

with unique_class as (
    select distinct
        handling_class
    from {{ ref('stg_batch_shipment') }}
    where handling_class is not null
),

add_surrogate_key as (
    select
        {{ dbt_utils.generate_surrogate_key(['handling_class']) }} as id_handlingClass,
        handling_class
    from unique_class
)

select
    id_handlingClass,
    handling_class
from add_surrogate_key
order by handling_class