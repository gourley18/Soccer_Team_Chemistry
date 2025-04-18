import numpy as np
import sqlite3

a = np.array([1,2,3])
b = np.array([3,2,1])
c = a + b
# print(c)

# create connection to sqlite db
connection = sqlite3.connect("""../db/lineups-data.db""") # Path to database

# create a cursor from the connection
cur = connection.cursor()

# Retreieve all matches data from 2001
data_matches = cur.execute("""
  SELECT * FROM matches
  WHERE date BETWEEN
  '2001-01-01' AND '2001-12-31';
  """)
print (data_matches.fetchall())
exit()

# SQL select query
data = cur.execute("SELECT * FROM lineups;")
print (data.__dir__())
exit()
player_id, match_id, team_id, player_type, sub_time = data.fetchone()

print("Cursor Options:")
print(cur.__dir__())
print()
print("Connection Options:")
print(connection.__dir__())
print()


connection.close()

print(match_id)


