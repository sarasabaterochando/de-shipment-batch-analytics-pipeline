{{ config(
    materialized='table'
) }}

with dim_data as (
    select distinct
        shipment_batch_ID,
        origin_facility,
        shipment_category,
        handling_class
    from {{ ref('stg_batch_shipment') }}
   
)

select
    {{ dbt_utils.generate_surrogate_key(['shipment_batch_ID']) }} as id_shipment_details,
    shipment_batch_ID,
    origin_facility,
    shipment_category,
    handling_class
from dim_data