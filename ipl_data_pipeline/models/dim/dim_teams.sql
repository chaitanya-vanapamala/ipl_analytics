{{
  config(
    materialized = 'table',
    )
}}

WITH raw_data AS (
    SELECT team1, team2 FROM {{ ref('stg_match_details') }}
)
SELECT ROW_NUMBER() OVER (ORDER BY name) AS team_id, name,  
{{ get_team_short_code('name') }} as short_name FROM
(SELECT DISTINCT team1 AS name FROM raw_data
UNION
SELECt DISTINCT team2 AS name FROM raw_data) teams