import sqlite3

def check_conn(connection):
  # Check an sqlite3 connection to the lineups db
  try:
    cursor = connection.cursor()
    cursor.execute("""
      SELECT * FROM matches
      WHERE date BETWEEN
      '2001-01-01' AND '2001-12-31';
      """)
    return True
  except Exception as ex:
    return False
     
if __name__=="__main__":
  try: # Successful when ran from top-level directory:: $ python3 .\testing_scripts\testDBConnection.py
    con = sqlite3.connect("""../db/lineups-data.db""") # May need to adjust file path if necessary
  except Exception as ex:
    pass
  
  try: # Successful when ran from testing_scripts directory:: $ python3 .\testDBConnection.py
    con = sqlite3.connect("""db/lineups-data.db""") # May need to adjust file path if necessary
  except Exception as ex:
    pass
  

  if check_conn(con):
    print("Connection to DB successful")
  else:
    print("Connection to DB NOT successful")


