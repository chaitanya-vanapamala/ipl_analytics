{{
  config(
    materialized = 'table',
    )
}}

WITH
    stg_deliveries AS (
        SELECT * FROM {{ ref('stg_deliveries') }}
    ),
    teams AS (
        SELECT * FROM {{ ref('dim_teams') }}
    ),
    players AS (
        SELECT * FROM {{ ref('dim_players') }}
    )

SELECT
    match_id,
    innings_no,
    bt.team_id as batting_team_id,
    is_super_over,
    over,
    delivery_no,
    pba.player_id as batter_player_id,
    pbo.player_id as bowler_player_id,
    pns.player_id as non_striker_player_id,
    runs_off_bat,
    extra_runs,
    total_runs,
    is_wicket,
    po.player_id as player_out_player_id,
    wicket_kind,
    {{ is_bowlers_wicket('wicket_kind') }} is_bowlers_wicket,
    pf.player_id as fielder_player_id
FROM 
    stg_deliveries d
LEFT JOIN teams bt
ON d.batting_team = bt.name
LEFT JOIN players pba
ON d.batter = pba.name 
LEFT JOIN players pbo
ON d.bowler = pbo.name
LEFT JOIN players pns
ON d.non_striker = pns.name
LEFT JOIN players po
ON d.player_out = po.name
LEFT JOIN players pf
ON d.fielder = pf.name