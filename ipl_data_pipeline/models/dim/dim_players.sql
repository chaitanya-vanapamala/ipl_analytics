{{
  config(
    materialized = 'table',
    )
}}

WITH raw_data AS (
    SELECT batter, bowler, non_striker, fielder FROM {{ ref('stg_deliveries') }}
),
players AS (
    SELECT DISTINCT batter as name FROM raw_data
    UNION
    SELECT DISTINCT non_striker as name FROM raw_data
    UNION
    SELECT DISTINCT bowler as name FROM raw_data
    UNION
    SELECT DISTINCT fielder as name FROM raw_data
)

SELECT ROW_NUMBER() OVER (ORDER BY name) AS player_id, name FROM players
