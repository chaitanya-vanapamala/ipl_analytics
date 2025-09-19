{% macro get_team_short_code(name) %}
    CASE 
        WHEN {{name}} = 'Deccan Chargers' THEN 'Deccan Chargers'
        WHEN {{name}} = 'Kings XI Punjab' THEN 'KXIP'
        ELSE regexp_replace(
            regexp_replace({{name}}, '\B(\w+)\b', '', 'g'),
            ' ', '', 'g'
        )
    END
{% endmacro %}
