{{ config(materialized='table') }}

with fact_base as (
    select
        l.shipment_batch_ID,
        l.dispatch_date,
        l.dispatch_time,
        l.completion_date,
        l.completion_time,
        l.origin_facility,
        l.shipment_category,
        l.handling_class,
        l.remarks,
        l.creation_data,
        h.package_class,
        h.total_weight_kg,
        h.load_percentage_bp,
        h.package_count
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
        fb.creation_data,
        fb.package_class,
        fb.total_weight_kg,
        fb.load_percentage_bp,
        fb.package_count,
        hc.id_handlingClass,
        orig.id_originFacility,
        pc.id_package_class,
        sc.id_shipment_category
    from 
        fact_base as fb
        left join {{ ref('dim_handling_class') }} as hc on fb.handling_class = hc.handling_class
        left join {{ ref('dim_origin_facility') }} as orig on orig.origin_facility = fb.origin_facility
        left join {{ ref('dim_package_class') }} as pc on pc.package_class = fb.package_class
        left join {{ ref('dim_shipment_category') }} as sc on sc.shipment_category = fb.shipment_category
)

select * from add_dimension_keys