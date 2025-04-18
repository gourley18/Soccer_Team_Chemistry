import multiprocessing
import numpy as np
import pandas as pd
import polars as pl
import time
import os

from Database import Database, select_matches


# Compile team chemistry data for a subset of the total matches to be analyzed (Chunk granularity is at the match level)
def process_chunk(df_chunk):
    # print(os.getpid()) # Uncomment to ensure multiple processes are running
    # val = df_chunk['home_team_id'] + df_chunk['away_team_id']
    match_id = df_chunk.iloc[0,0]
    match_date = df_chunk.iloc[0,1]
    home_team_id = df_chunk.iloc[0,2]
    away_team_id = df_chunk.iloc[0,3]
    home_goals_scored = df_chunk.iloc[0,4]
    away_goals_scored = df_chunk.iloc[0,5]
    db = Database().connect("""db/lineups-data.db""") # Connect to db


    is_home_team=True # Keep track of home team or away team
    for team_id in [home_team_id, away_team_id]:
      # Get each player_id for the Home Team
      home_team_player_ids = db.cursor().execute(
        f"""
        SELECT l.player_id
        FROM lineups l
        WHERE l.match_id={match_id}
          AND l.team_id={team_id}
          AND l.player_type='Starter';
        """)
      
      # Get the player ids of the 11 starters
      home_starters = np.zeros(11, dtype=int)
      iter = -1
      for id in home_team_player_ids:
        iter += 1
        if (iter > 10):
          print("Returning Empty List")
          return [] # Return an empty set
        home_starters[iter] = id[0]

      # sorted lowest id to highest
      home_starters = np.sort(home_starters)
      
      # Debug Print statments
      # print (f"match id: {match_id}")
      # print (f"home staters: {home_starters}")

      # Represents Earliest Match in the database
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
            team_chem_array[array_col][array_row] = len(set_intersection)

      print(f'm: {match_id}, t: {team_id}')
      # print(team_chem_array)
      # Get the indices of the upper triangular elements
      iu = np.triu_indices(team_chem_array.shape[0], k=1)

      # Extract the values using the indices
      features = team_chem_array[iu]
      # print(features)

      if(is_home_team):
        features_home=features
        is_home_team=False

      # feature_columns = [f"feature_{i+1}" for i in range(55)]

      # # Create the DataFrame
      # df = pl.DataFrame({
      #     "team_id": [home_team_id],  # Single value as a list
      #     **{col: [val] for col, val in zip(feature_columns, features)},  # Unpacking features
      #     "goals_scored": [home_goals_scored]  # Single value as a list
      # })

      # print(df)

  
  
    # return pd.DataFrame({'match_id':df_chunk['match_id'], 'val':val})
    return [
      (match_id, home_team_id, features_home, home_goals_scored, away_goals_scored),
      (match_id, away_team_id, features, away_goals_scored, home_goals_scored)
    ]


def main():
    
    start = time.time() # Start timing for benchmarking

    NUM_MATCHES = None # Select NONE to not limit query (50 means that it will only return the first 50 results from that year)
    YEAR = 2011 # set the YEAR variable to the year you want to get the data for
    NUM_PROCS = multiprocessing.cpu_count() # This sets the number of processors to the number on your computer
    # NUM_PROCS =  # 12

    # Query matches data from the database
    matches = select_matches(start_date=f'{YEAR}-01-01', end_date=f'{YEAR}-12-31', limit=NUM_MATCHES)

    # put the matches data (query result) into a pandas dataframe
    df = pd.DataFrame(matches.fetchall())
    df.columns = ["match_id", "date", "home_team_id", "away_team_id", "home_team_goal", "away_team_goal"]

    # Divide the input data into chunks to send to the processes
    chunk_size = 1 # if using a value other than 1, we need to modify our process_chunk function
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
    # print (chunks) # Uncomment to verify what the chunks look like
    
    print(f'beginning parallel compilation')
    print(f'compiling data for {"all" if NUM_MATCHES == None else NUM_MATCHES} matches in {YEAR}')
    print(f'with {NUM_PROCS} processors')


    # Begin Parallelism
    pool = multiprocessing.Pool(processes = NUM_PROCS) # create task pool
    results = pool.imap_unordered(process_chunk, chunks)
    pool.close() # signify that we are not adding any more tasks to the pool
    pool.join() # blocking, waits for the entire task pool to be dried up
    # End Parallelism

    # Flatten the results (since each call returns two rows)
    data = [row for match in results if match for row in match]

    match_ids, team_ids, feature_lists, goals_scored, goals_allowed = zip(*data)
    feature_columns = [f"feature_{i+1}" for i in range(55)]
    df = pl.DataFrame({
      "match_id": match_ids,  # Each match_id as a row
      "team_id": team_ids,  # Each team_id as a row
      **{col: [row[i] for row in feature_lists] for i, col in enumerate(feature_columns)},  # Features as separate columns
      "goals_scored": goals_scored,  # Goals scored column
      "goals_allowed": goals_allowed  # Goals allowed column
    })
    print(df)


    end = time.time() # end timing for parallel metrics

    # Handle outputting the results 
    # for result in results:
    #   if result is not None:
    #     print()
    #     print (f'match_id: {result[0]}')
    #     print (result[1])

    print (f'it took {end - start} secs to create arrays for {"all" if NUM_MATCHES == None else NUM_MATCHES } matches in {YEAR} using {NUM_PROCS} processes')
    print()

    print("writing csv")
    
    df.write_csv(f"project1_{YEAR}_{"all" if NUM_MATCHES == None else NUM_MATCHES }.csv")


if __name__ == '__main__':
    main()