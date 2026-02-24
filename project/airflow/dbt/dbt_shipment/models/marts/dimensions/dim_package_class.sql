{{ config(
    materialized='table'
) }}

with unique_package_classes as (
    select distinct
        package_class
    from {{ ref('stg_batch_metrics') }}
    where package_class is not null
),

add_surrogate_key as (
    select
        {{ dbt_utils.generate_surrogate_key(['package_class']) }} as id_package_class,
        package_class
    from unique_package_classes
)

select
    id_package_class,
    package_class
from add_surrogate_key
order by package_class