{% macro process_city_name(city_name) %}

    CASE
        WHEN {{city_name}} = 'Bengaluru' THEN 'Bangalore'
        WHEN {{city_name}} = 'Navi Mumbai' THEN 'Mumbai'
        WHEN {{city_name}} = 'Mohali' THEN 'New Chandigarh'
        WHEN {{city_name}} = 'Dubai' THEN 'Sharjah'
        WHEN {{city_name}} is NULL THEN 'Sharjah'
        ELSE {{city_name}}
    END

{% endmacro %}