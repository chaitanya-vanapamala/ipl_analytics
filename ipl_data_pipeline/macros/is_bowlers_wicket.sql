{% macro is_bowlers_wicket(kind) %}
  CASE
    WHEN {{kind}} = 'bowled' OR
    {{kind}} = 'caught and bowled' OR
    {{kind}} = 'lbw' OR
    {{kind}} = 'hit wicket' OR
    {{kind}} = 'stumped' OR
    {{kind}} = 'caught' THEN 1
    WHEN {{kind}} is NULL THEN NULL
    ELSE 0
  END
{% endmacro %}