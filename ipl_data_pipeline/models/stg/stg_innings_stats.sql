WITH raw_data AS (
    SELECT match_id, 
    {{ process_team_name('batting_team') }} batting_team,
    innings_no::INTEGER AS innings_no,
    is_super_over::INTEGER AS is_super_over,
    runs_off_bat::INTEGER AS runs_off_bat, 
    extra_runs::INTEGER AS extra_runs, 
    total_runs::INTEGER AS total_runs, 
    is_wicket::INTEGER AS is_wicket,
    delivery_no::DECIMAL AS delivery_no
    FROM raw_ball_by_ball
)

SELECT {{ dbt_utils.generate_surrogate_key(['match_id']) }} AS match_id, 
innings_no, MAX(batting_team) as batting_team,
MAX(is_super_over) as is_super_over, 
SUM(runs_off_bat) as runs_off_bat, SUM(extra_runs) as extras, 
SUM(total_runs) AS total_runs, SUM(is_wicket) as wickets, 
SUM(CASE WHEN runs_off_bat = 4 or extra_runs = 5 THEN 1 ELSE 0 END) no_of_fours,
SUM(CASE WHEN runs_off_bat = 6 or extra_runs = 7 THEN 1 ELSE 0 END) no_of_sixes,
SUM(CASE WHEN runs_off_bat >= 4 or extra_runs >= 5 THEN 1 ELSE 0 END) no_of_boundries,
COUNT(1) as total_deliveries,
CASE WHEN max(delivery_no) >= 19.6 THEN 20 ELSE max(delivery_no) END as total_overs
FROM raw_data
GROUP BY match_id, innings_no
