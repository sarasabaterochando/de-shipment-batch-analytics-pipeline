{{ config(
    materialized='table'
) }}

select
    {{ dbt_utils.generate_surrogate_key([
        'rr.package_class',
        'rr.rule_index'
    ]) }} AS id_routing_rule,
    pc.id_package_class,
    rr.rule_index,
    rr.rule_metric,
    rr.min_threshold,
    rr.max_limit
from {{ ref('int_routing_rules') }} as rr
left join {{ ref('dim_package_class') }} as pc on pc.package_class = rr.package_class