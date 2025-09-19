{% macro process_team_name(name) %}
    CASE 
        WHEN {{name}} = 'Rising Pune Supergiant' THEN 'Rising Pune Supergiants'
        WHEN {{name}} = 'Royal Challengers Bengaluru' THEN 'Royal Challengers Bangalore'
        WHEN {{name}} = 'Sunrisers Hyderabad' THEN 'Sun Risers Hyderabad'
        WHEN {{name}} = 'Punjab Kings' THEN 'Kings XI Punjab'
        ELSE {{name}}
    END
{% endmacro %}