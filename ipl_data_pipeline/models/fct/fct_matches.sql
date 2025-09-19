{{
  config(
    materialized = 'table',
    )
}}

WITH 
    raw_data AS (
        SELECT * FROM {{ ref('stg_match_details') }}
    ),
    dim_venue AS (
        SELECT * FROM {{ ref('dim_venue') }}
    ),
    dim_teams AS (
        SELECT * FROM {{ ref('dim_teams') }}
    ),
    dim_players AS (
        SELECT * FROM {{ ref('dim_players') }}
    ),
    match_data AS (
        SELECT
            match_id, match_date, season, 
            match_type, dim_venue.venue_id, 
            t1.team_id as team1_id, t2.team_id as team2_id,
            twt.team_id as toss_winner_id, wt.team_id as winner_team_id,
            win_by_runs, win_by_wickets, pom1.player_id as player_of_match_id  
        FROM raw_data
        LEFT JOIN dim_venue
            ON raw_data.venue = dim_venue.name
        LEFT JOIN dim_teams AS t1
            ON raw_data.team1 = t1.name
        LEFT JOIN dim_teams AS t2
            ON raw_data.team2 = t2.name
        LEFT JOIN dim_teams AS twt
            ON raw_data.toss_winner = twt.name
        LEFT JOIN dim_teams AS wt
            ON raw_data.winner = wt.name
        LEFT JOIN dim_players pom1
            ON raw_data.player_of_match_1 = pom1.name
    )

SELECT * FROM match_data
