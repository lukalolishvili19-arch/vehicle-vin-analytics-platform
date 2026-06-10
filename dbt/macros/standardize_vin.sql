{% macro standardize_vin(column_name) %}
    upper(trim({{ column_name }}))
{% endmacro %}
