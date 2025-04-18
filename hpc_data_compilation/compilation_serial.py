import numpy as np
import pandas as pd
import time

from Database import Database, select_matches


# Compile data to create a team chemistry array
def create_chemistry_array_serial(match_id, match_date, home_team_id, away_team_id):
    db = Database().connect("""db/lineups-data.db""")
    # Get each player_id for the Home Team
    home_team_player_ids = db.cursor().execute(
      f"""
      SELECT l.player_id
      FROM lineups l
      WHERE l.match_id={match_id}
        AND l.team_id={home_team_id}
        AND l.player_type='Starter';
      """)
    
    # Get the player ids of the 11 starters
    home_starters = np.zeros(11, dtype=int)
    iter = -1
    for id in home_team_player_ids:
      iter += 1
      if (iter > 10):
        return
      home_starters[iter] = id[0]

    # sorted lowest id to highest
    home_starters = np.sort(home_starters)
    
    # print (f"match id: {match_id}")
    # print (f"home staters: {home_starters}")
  

    global_start_date = '2001-01-01'

    # Initialize an 11 x 11 array with all zeros
    team_chem_array = np.zeros((11,11), dtype=int)
    
    # Get data for players playing time
    home_playing_time = []

    # Compile lineup data for each starter on the home team
    for id in home_starters:
      # Query the database for lineup data pertaining to next calculations
      player_lineup = db.cursor().execute(
        f"""
        SELECT
          l.player_id,
          l.match_id,
          l.team_id,
          l.player_type,
          l.sub_time,
          m.date
        FROM lineups l
        JOIN matches m
          ON m.match_id=l.match_id
        WHERE
          m.date Between '{global_start_date}' AND '{match_date}'
          AND l.player_id={id}
        ORDER BY date;
        """)
      
      # Get the player ids of the 11 starters
      lineup_data = set()
      z = -1
      for data in player_lineup:
        z += 1
        d = (data[1], data[2])
        lineup_data.add(d)
      
      # print (lineup_data)
      home_playing_time.append(lineup_data)
    
    # Loop through rows and columns of the team chemistry array
    for array_col in range(11):
      for array_row in range(11):
        # We only want to iterate through the upper triangular portion of the playing time array
        if array_col >= array_row:
          # print(f"skipping row: {array_row} col {array_col}")
          pass
        else:
          # Calculate number of minutes played todether between the 2 home players
          set_intersection = home_playing_time[array_col].intersection(home_playing_time[array_row])
          team_chem_array[array_col][array_row] = len(set_intersection)*90
   
    print(f'm: {match_id}')
    print(team_chem_array)
    print()
  
  
    # return pd.DataFrame({'match_id':df_chunk['match_id'], 'val':val})
    return match_id, team_chem_array


def main():
    
  NUM_MATCHES = 200
  start = time.time() # Start timing for benchmarking

  # Query matches data from the database
  matches = select_matches(start_date='2015-01-01', end_date='2024-01-01', limit=NUM_MATCHES)

  # put the matches data (query result) into a pandas dataframe
  df = pd.DataFrame(matches.fetchall())
  df.columns = ["match_id", "date", "home_team_id", "away_team_id", "home_team_goal", "away_team_goal"]

  for row in df.itertuples():
    create_chemistry_array_serial(row.match_id, row.date, row.home_team_id, row.away_team_id)

  print(f'beginning serial compilation')
  print(f'compiling data for {NUM_MATCHES} matches')

  end = time.time() # end timing for  metrics

  print (f'it took {end - start} secs to create arrays for {NUM_MATCHES} matches serially')


if __name__ == '__main__':
    main()