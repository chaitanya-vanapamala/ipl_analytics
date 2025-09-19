{% macro process_venue(venue) %}
    CASE
        WHEN INSTR(venue, ',') > 0 THEN SUBSTRING(venue, 1, INSTR(venue, ',') - 1)
        ELSE venue
    END
{% endmacro %}