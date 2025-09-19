{{
  config(
    materialized = 'table',
    )
}}

WITH raw_data AS (
    SELECT DISTINCT venue, city
    FROM {{ ref('stg_match_details') }}
)

SELECT
ROW_NUMBER() OVER (ORDER BY venue, city) AS venue_id, 
city,
venue as name
FROM raw_data