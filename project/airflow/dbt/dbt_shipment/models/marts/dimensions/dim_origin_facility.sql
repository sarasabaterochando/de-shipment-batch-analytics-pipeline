{{ config(
    materialized='table'
) }}

with unique_facilities as (
    select distinct
        origin_facility
    from {{ ref('stg_batch_shipment') }}
    where origin_facility is not null
),

add_surrogate_key as (
    select
        {{ dbt_utils.generate_surrogate_key(['origin_facility']) }} as id_originFacility,
        origin_facility
    from unique_facilities
)

select
    id_originFacility,
    origin_facility
from add_surrogate_key
order by origin_facility