{{
  config(
    materialized = 'table',
    )
}}

WITH
    innings AS (
        SELECT * FROM {{ ref('stg_innings_stats') }}
    ),
    teams AS (
        SELECT * FROM {{ ref('dim_teams') }}
    )
    
SELECT 
    match_id, innings_no, bt.team_id as batting_team_id, is_super_over, runs_off_bat, 
    extras, total_runs, wickets, no_of_fours, no_of_sixes, 
    no_of_boundries, total_deliveries, total_overs
FROM innings
JOIN teams as bt
ON innings.batting_team = bt.name
