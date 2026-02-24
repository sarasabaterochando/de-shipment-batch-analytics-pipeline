{{ config(
    materialized='view'
) }}

with source as (
    select 
        shipment_batch_ID,
        package_class,
        total_weight_kg,
        load_percentage_bp,
        package_count,
        routing_rules,
        destination_hubs
    from 
        {{ source('raw_shipment', 'fact_batch_shipment') }}
),
renamed as (
    select
        shipment_batch_ID,
        {{ format_initcap_spaces('package_class') }} as package_class,
        total_weight_kg,
        load_percentage_bp,
        package_count,
        {{ format_initcap_spaces('routing_rules') }} as routing_rules,
        destination_hubs
    from 
        source

)

select * from renamed