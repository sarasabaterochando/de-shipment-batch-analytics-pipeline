{{ config(
    materialized='view'
) }}

SELECT distinct
    shipment_batch_id,
    package_class,
    SAFE_CAST(hub AS INT64) AS destination_hub_id
FROM {{ ref('stg_batch_metrics') }},
UNNEST(SPLIT(destination_hubs, '|')) AS hub