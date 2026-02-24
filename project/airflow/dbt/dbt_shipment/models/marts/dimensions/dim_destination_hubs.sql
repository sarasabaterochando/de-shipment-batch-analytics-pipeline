{{ config(
    materialized='table'
) }}

SELECT
    {{ dbt_utils.generate_surrogate_key([
        'shipment_batch_id', 
        'package_class', 
        'destination_hub_id'
    ]) }} AS id_shipment_hub,
    shipment_batch_id,
    package_class,
    destination_hub_id
FROM {{ ref('int_destination_hubs') }}