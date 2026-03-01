{{ config(
    materialized='view'
) }}

with source as (
    select distinct
        shipment_batch_ID,
        dispatch_date,
        dispatch_time,
        completion_date,
        completion_time,
        origin_facility_ID,
        shipment_category,
        handling_class,
        remarks
    from 
        {{ source('raw_shipment', 'dim_batch_shipment') }}
),

renamed as (
    select
        shipment_batch_ID,
        dispatch_date,
        dispatch_time,
        completion_date,
        completion_time,
        {{ format_initcap_spaces('origin_facility_ID') }} as origin_facility,
        {{ format_initcap_spaces('shipment_category') }} as shipment_category,
        initcap(handling_class) as handling_class,
        remarks
    from 
        source
)

select * from renamed

