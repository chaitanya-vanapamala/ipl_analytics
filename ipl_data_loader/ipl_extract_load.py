import json
import pandas as pd
import os
from glob import glob
import duckdb

def flatten_json_to_df(file_id, json_data):
    """
    Parses nested cricket JSON data and returns a flattened Pandas DataFrame.
    """
    match_data = []

    # Extract match-level information
    info = json_data.get('info', {})
    season = info.get('season')
    match_no = info.get('event', {}).get('match_number')
    stage = info.get('event', {}).get('stage')

    if match_no is None:
        match_no = info.get('event', {}).get('stage')

    match_type = stage if stage else 'League'

    match_date = info.get('dates', [])[0] if info.get('dates') else None
    
    match_id = str(match_date).replace('-', '') + '_' + str(season) + '_' + str(match_no) 
    venue = info.get('venue')
    city = info.get('city')
    team1 = info.get('teams', [])[0] if info.get('teams') else None
    team2 = info.get('teams', [])[1] if info.get('teams') else None


    winner = info.get('outcome', {}).get('winner')    
    result = 'win'

    outcome_by = info.get('outcome', {}).get('by', {})
    win_by_runs = outcome_by.get('runs')
    win_by_wickets = outcome_by.get('wickets')

    if winner is None:
        result = info.get('outcome', {}).get('result', {})
        winner = info.get('outcome', {}).get('eliminator', {})

    toss_info = info.get('toss', {})
    toss_winner = toss_info.get('winner')
    toss_decision = toss_info.get('decision')

    player_of_match_list = info.get('player_of_match', [])
    player_of_match_1 = player_of_match_list[0] if len(player_of_match_list) > 0 else None
    player_of_match_2 = player_of_match_list[1] if len(player_of_match_list) > 1 else None
    player_of_match_3 = player_of_match_list[2] if len(player_of_match_list) > 2 else None

    print(f"Processing ball data for {match_id} : {team1} vs {team2}")

    innings_no = 0
    # Iterate through innings
    for inning in json_data.get('innings', []):
        innings_no += 1
        team_name = inning.get('team')
        is_super_over = inning.get('super_over', False)
        
        # Iterate through overs in the inning
        for over_data in inning.get('overs', []):
            over_number = over_data.get('over')
            
            ball_count = 0
            # Iterate through deliveries in the over
            for delivery in over_data.get('deliveries', []):
                # Extract runs and player details for this ball
                ball_count += 1
                runs = delivery.get('runs', {})
                batter = delivery.get('batter')
                bowler = delivery.get('bowler')
                non_striker = delivery.get('non_striker')

                # Check for a wicket
                wicket_list = delivery.get('wickets', [])
                is_wicket = 1 if wicket_list else 0

                player_out = None
                wicket_kind = None
                fielder = None

                if is_wicket:
                    wicket_info = wicket_list[0]
                    player_out = wicket_info.get('player_out')
                    wicket_kind = wicket_info.get('kind')
                    
                    # --- New code to extract fielder name ---
                    if 'fielders' in wicket_info and wicket_info['fielders']:
                        fielder_info = wicket_info['fielders'][0]
                        fielder = fielder_info.get('name')


                # Create a record for each ball
                match_data.append({
                    'file_id': file_id,
                    'match_id': match_id,
                    'match_type' : match_type,
                    'ipl_season' : season,
                    'match_date': match_date,
                    'venue': venue,
                    'city': city,
                    'team1': team1,
                    'team2': team2,
                    'toss_winner': toss_winner,
                    'toss_decision': toss_decision,
                    'outcome': result,
                    'winner': winner,
                    'win_by_runs': win_by_runs,
                    'win_by_wickets': win_by_wickets,
                    'player_of_match_1': player_of_match_1,
                    'player_of_match_2': player_of_match_2,
                    'player_of_match_3': player_of_match_3,
                    'batting_team': team_name,
                    'innings_no': innings_no,
                    'is_super_over': is_super_over,
                    'over': over_number,
                    'delivery_no': over_number + ball_count / 10,
                    'batter': batter,
                    'bowler': bowler,
                    'non_striker': non_striker,
                    'runs_off_bat': runs.get('batter', 0),
                    'extra_runs': runs.get('extras', 0),
                    'total_runs': runs.get('total', 0),
                    'is_wicket': is_wicket,
                    'player_out': player_out,
                    'wicket_kind': wicket_kind,
                    'fielder': fielder
                })

    return match_id, pd.DataFrame(match_data)


def load_data_to_db(conn, match_id, df):

    result = conn.execute(f"SELECT table_name FROM information_schema.tables WHERE table_name = '{table_name}'").fetchall()
    # result = conn.execute(f"SELECT view_name FROM duckdb_views() WHERE view_name = '{table_name}'").fetchall()

    if result:
        conn.append(table_name, df)
        print(f"Successfully appended data for match id {match_id}")
    else:
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
        print(f"Table '{table_name}' created from match data of {match_id}")



if __name__ == "__main__":
    # Define file paths
    base_dir = r'E:/Projects/Personal/ipl_analytics'
    in_data_path = f'{base_dir}/raw_data/ipl_male_json/'
    out_data_path = f'{base_dir}/raw_data/ipl_csv/'
    
    db_path = f'{base_dir}/ipl_dwh/dev.duckdb'
    table_name = 'raw_ball_by_ball'

    # duck db connection
    conn = duckdb.connect(database=db_path)

    pattern = os.path.join(in_data_path, '*.json')
    json_files = glob(pattern)
    total_files = len(json_files)

    print(f"Total no.of files : {total_files}")
    count = 0
    out_df = None

    total_rows = 0

    for input_json_file in json_files:
        count += 1
        print(f"\n\nProcessing File {count}/{total_files} : {input_json_file}")
        file_name = os.path.basename(input_json_file).split(".")[0]

        if not os.path.exists(input_json_file):
            print(f"Error: The file {input_json_file} was not found.")
        else:
            with open(input_json_file, 'r') as f:
                ipl_data = json.load(f)

            match_id, df = flatten_json_to_df(file_name, ipl_data)
            str_cols = ['file_id', 'match_id', 'match_type', 'ipl_season', 'venue', 'city',
                        'team1', 'team2', 'toss_winner', 'toss_decision', 'outcome', 'winner',
                        'player_of_match_1', 'player_of_match_2', 'player_of_match_3', 'batting_team',
                        'batter', 'bowler', 'non_striker', 'player_out', 'wicket_kind', 'fielder']
            date_cols = ['match_date']
            int_cols = ['win_by_runs', 'win_by_wickets', 'innings_no', 'over', 'delivery_no', 
                        'runs_off_bat', 'extra_runs', 'total_runs']
            
            df[str_cols] = df[str_cols].astype(str).replace('None', None)
            
            df[date_cols] = df[date_cols].apply(pd.to_datetime)
            for ic in int_cols:
                df[ic] = pd.to_numeric(df[ic], errors='coerce')

            match_id = match_id.replace("/", "_")
            output_csv_file = f"{out_data_path}{match_id}.csv"

            total_rows += df.shape[0]
            # Save the DataFrame to a CSV file
            df.to_csv(output_csv_file, index=False)
            print(f"Successfully converted {input_json_file} to {output_csv_file}")
            print(f"DataFrame shape: {df.shape}")
            print(f"Loading data into db...")
            load_data_to_db(conn, match_id, df)

    print(f"\n\nTotal rows from json data : {total_rows}")
    result = conn.execute(f"SELECT COUNT(1) FROM {table_name}").fetchone()
    print(f"Total rows written into db : {result[0]}")

    conn.close()

            
            