{{ config(
    materialized='table'
) }}


SELECT
    {{ dbt_utils.generate_surrogate_key([
        'shipment_batch_id',
        'package_class',
        'rule_index'
    ]) }} AS id_routing_rule,
    shipment_batch_id,
    package_class,
    rule_index,
    rule_metric,
    rule_context,
    min_threshold,
    max_limit
FROM {{ ref('int_routing_rules') }}






