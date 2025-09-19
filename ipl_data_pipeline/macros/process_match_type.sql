{% macro process_match_type(match_type) %}

  CASE 
    WHEN {{match_type}} like 'Qualifier%' 
    OR {{match_type}} like 'Elimination%' 
    OR {{match_type}} like 'Eliminator%'
    OR {{match_type}} like 'Semi%'
    OR {{match_type}} like '3rd Place%' THEN 'play off'
    ELSE LOWER({{match_type}})
    END

{% endmacro %}