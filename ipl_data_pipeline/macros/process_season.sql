{% macro process_season(match_date) %}
  date_part('year', match_date)
{% endmacro %}
