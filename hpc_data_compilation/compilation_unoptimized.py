import numpy as np
import pandas as pd
import time

from Database import DBManager, select_matches


# Compile data to create a team chemistry array
def create_chemistry_array_serial(match_id, match_date, home_team_id, away_team_id):
  db = DBManager().connect("""db/lineups-data.db""")
  cursor = db.cursor()
  # Get each player_id for the Home Team
  home_team_player_ids = cursor.execute(
    f"""
    SELECT l.player_id
    FROM lineups l
    WHERE l.match_id={match_id}
      AND l.team_id={home_team_id}
      AND l.player_type='Starter';
    """)
  
  # Get the player ids of the 11 starters
  home_starters=[]
  for id in home_team_player_ids:
    home_starters.append(id[0])
  # home_starters = home_team_player_ids.fetchall()
  if len(home_starters) != 11:
    return

  # sorted lowest id to highest
  home_starters.sort()
  
  # print (f"match id: {match_id}")
  # print (f"home staters: {home_starters}")

  global_start_date = '2001-01-01'

  # Initialize an 11 x 11 array with all zeros
  team_chem_array = np.zeros((11,11))

  array_col: int = -1
  # Loop through the home starters to compare against
  for id1 in home_starters:
    array_col += 1
    
    array_row: int = -1
    # Loop through home starters to compare to
    for id2 in home_starters:
      array_row += 1
      if id2 >= id1:
        # We only want to iterate through the upper triangular portion of the playing time array
        pass
      else:
        # Query the database for data pertaining to next calculations# create a cursor from the connection
        cursor_1 = db.cursor()
        player_1_lineup = cursor_1.execute(
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
            AND l.player_id={id1}
          ORDER BY date;
          """)

        # These rows represent games with lineup data f
        iter = -1

        # Loop through the matches that player 1 has played in
        for row1 in player_1_lineup:
          iter +=1
          # Query the database for data pertaining to next calculations
          cursor_2 = db.cursor()
          player_2_lineup = cursor_2.execute(
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
              AND l.player_id={id2}
            ORDER BY date;
            """)

          # Loop through the matches that player 2 has played in
          for row2 in player_2_lineup:
            # Check if match ids match!
            if row1[1] == row2[1] and row1[2] == row2[2]:
              # assumes both are starters (for simplility sake)
              team_chem_array[array_row][array_col] += 90
              # They already played this game together, so move onto the next
              break

  # Print team chemistry array to the console as they are created
  print(f'm: {match_id}')
  print(team_chem_array)
  print()

  return team_chem_array


def main():
    
  NUM_MATCHES = 10
  start = time.time() # Start timing for benchmarking

  # Query matches data from the database
  matches = select_matches(start_date='2015-01-01', end_date='2024-01-01', limit=NUM_MATCHES)

  # put the matches data (query result) into a pandas dataframe
  df = pd.DataFrame(matches.fetchall())
  df.columns = ["match_id", "date", "home_team_id", "away_team_id", "home_team_goal", "away_team_goal"]

  print(f'beginning serial compilation')
  print(f'compiling data for {NUM_MATCHES} matches')
  
  for row in df.itertuples():
    create_chemistry_array_serial(row.match_id, row.date, row.home_team_id, row.away_team_id)


  end = time.time() # end timing for  metrics

  print (f'it took {end - start} secs to create arrays for {NUM_MATCHES} matches serially using the initial unoptimized alogithm')


if __name__ == '__main__':
    main()