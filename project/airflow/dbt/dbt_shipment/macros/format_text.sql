{% macro format_initcap_spaces(column_name) %}
    (
        SELECT
            STRING_AGG(
                CONCAT(UPPER(SUBSTR(word, 1, 1)), LOWER(SUBSTR(word, 2))),
                ' '
                ORDER BY offset
            )
        FROM
            UNNEST(SPLIT(REGEXP_REPLACE({{ column_name }}, r'_', ' '), ' ')) AS word
            WITH OFFSET offset
    )
{% endmacro %}