{{ config(
    materialized='view'
) }}


WITH source AS (
    SELECT
        package_class,
        SPLIT(routing_rules, '|') AS parts
    FROM {{ ref('stg_batch_metrics') }}
),

unnested AS (
    SELECT
        package_class,
        part,
        offset
    FROM source,
    UNNEST(parts) AS part WITH OFFSET AS offset
),

grouped AS (
    SELECT
        package_class,
        CAST(FLOOR(offset / 4) AS INT64)            AS rule_index,
        initcap(MAX(IF(MOD(offset, 4) = 0, part, NULL)))    AS rule_metric,
        MAX(IF(MOD(offset, 4) = 2, part, NULL))     AS min_threshold_raw,
        MAX(IF(MOD(offset, 4) = 3, part, NULL))     AS max_limit_raw
    FROM unnested
    GROUP BY 1, 2
)

SELECT
    {{ format_initcap_spaces('package_class') }} as package_class,
    rule_index,
    rule_metric,
    SAFE_CAST(min_threshold_raw AS FLOAT64)  AS min_threshold,
    SAFE_CAST(max_limit_raw    AS FLOAT64)  AS max_limit
FROM grouped
ORDER BY  package_class, rule_index