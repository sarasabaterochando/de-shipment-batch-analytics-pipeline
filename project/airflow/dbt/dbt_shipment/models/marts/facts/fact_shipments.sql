{{ config(materialized='table') }}

with fact_base as (
    select
        l.shipment_batch_ID,
        l.dispatch_date,
        l.dispatch_time,
        l.completion_date,
        l.completion_time,
        l.remarks,
        h.package_class,
        h.total_weight_kg,
        h.load_percentage_bp,
        h.package_count,
        h.number_destination_hubs
    from 
        {{ ref('stg_batch_shipment') }} as l
        left join {{ ref('stg_batch_metrics') }} as h on h.shipment_batch_ID = l.shipment_batch_ID
),

add_dimension_keys as (
    select
        fb.shipment_batch_ID,
        fb.dispatch_date,
        fb.dispatch_time,
        fb.completion_date,
        fb.completion_time,
        fb.remarks,
        fb.total_weight_kg,
        fb.load_percentage_bp,
        fb.package_count,
        fb.number_destination_hubs,
        pc.id_package_class,
        sd.id_shipment_details
    from 
        fact_base as fb
        left join {{ ref('dim_shipment_details') }} as sd on sd.shipment_batch_ID = fb.shipment_batch_ID
        left join {{ ref('dim_package_class') }} as pc on pc.package_class = fb.package_class
)

select
    id_shipment_details,
    id_package_class,
    shipment_batch_ID,
    dispatch_date,
    dispatch_time,
    completion_date,
    completion_time,
    remarks,
    total_weight_kg,
    load_percentage_bp,
    package_count,
    number_destination_hubs
from add_dimension_keys