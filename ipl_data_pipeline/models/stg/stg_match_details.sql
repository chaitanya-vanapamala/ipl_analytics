WITH raw_data AS (
    SELECT
        match_id, 
        MAX(match_type) AS match_type,
        MAX(ipl_season) AS season,
        MAX(match_date) AS match_date,
        MAX(venue) AS venue,
        MAX(city) AS city,
        MAX(team1) AS team1,
        MAX(team2) AS team2,
        MAX(toss_winner) AS toss_winner,
        MAX(toss_decision) AS toss_decision,
        MAX(outcome) as outcome,
        MAX(winner) as winner,
        MAX(win_by_runs) as win_by_runs,
        MAX(win_by_wickets) as win_by_wickets,
        MAX(player_of_match_1) as player_of_match_1,
        MAX(player_of_match_2) as player_of_match_2,
        MAX(player_of_match_3) as player_of_match_3
    FROM raw_ball_by_ball
    GROUP BY match_id
)


SELECT
    {{ dbt_utils.generate_surrogate_key(['match_id']) }} AS match_id,
    {{ process_match_type('match_type') }} AS match_type,
    {{ process_season('match_date') }} AS season, 
    match_date, 
    {{ process_venue('venue') }} AS venue,
    {{ process_city_name('city') }} AS city,
    {{ process_team_name('team1') }} AS team1,
    {{ process_team_name('team2') }} AS team2,
    {{ process_team_name('toss_winner') }} AS toss_winner,
    toss_decision, outcome,
    {{ process_team_name('winner') }} as winner, 
    win_by_runs, win_by_wickets,
    player_of_match_1, player_of_match_2, player_of_match_3
FROM raw_data
