SELECT 
    {{ dbt_utils.generate_surrogate_key(['match_id']) }} AS match_id,
    innings_no::INTEGER AS innings_no,
    batting_team,
    is_super_over::INTEGER AS is_super_over,
    over::INTEGER AS over,
    delivery_no::DECIMAL AS delivery_no,
    batter,
    bowler,
    non_striker,
    runs_off_bat::INTEGER AS runs_off_bat,
    extra_runs::INTEGER AS extra_runs,
    total_runs::INTEGER AS total_runs,
    is_wicket::INTEGER AS is_wicket,
    player_out,
    wicket_kind,
    fielder
FROM raw_ball_by_ball
