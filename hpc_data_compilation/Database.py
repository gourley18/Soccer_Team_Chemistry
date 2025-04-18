import sqlite3


class Database:
  """
  This is a Singleton class that establishes a connection to a sqlite database
  """
  _instance = None

  def __new__(cls, *args, **kwargs):
    if cls._instance is None:
      cls._instance = super().__new__(cls, *args, **kwargs)
      cls._instance.connection = None
    return cls._instance

  def connect(self, db_name):
    if self.connection is None:
      self.connection = sqlite3.connect(db_name)
    return self.connection

  def close(self):
    if self.connection is not None:
      self.connection.close()
      self.connection = None

      # Retreieve all matches data from a specified date range

      
def select_matches(start_date, end_date, limit = None):
  db = Database().connect("""db/lineups-data.db""")
  cursor = db.cursor()
  if (limit is None):
    match_table = cursor.execute(
      f"""
      SELECT
        match_id,
        date, 
        home_team_id,
        away_team_id,
        home_team_goal,
        away_team_goal
      FROM matches
      WHERE date BETWEEN
      '{start_date}' AND '{end_date}'
      ORDER BY date ASC;
      """)
  else:
    match_table = cursor.execute(
      f"""
      SELECT
        match_id,
        date, 
        home_team_id,
        away_team_id,
        home_team_goal,
        away_team_goal
      FROM matches
      WHERE date BETWEEN
      '{start_date}' AND '{end_date}'
      ORDER BY date ASC
      Limit {limit};
      """)
  return match_table