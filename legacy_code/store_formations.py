import sqlite3
import pickle
from tqdm import tqdm

conn = sqlite3.connect('data/lineups-data.db')
cursor = conn.cursor()

formations = []
with open('formations.pkl', 'rb') as f:
    formations = pickle.load(f)

unique_formations = set()
unique_formations_dict = {}
valid_formations = []
partially_valid = []
for f in tqdm(formations):
    if isinstance(f, tuple):
        if f[1] is not None and f[2] is not None:
            m1 = [n for n in f[1].split('-')]
            m2 = [n for n in f[2].split('-')]
            match1 = True
            match2 = True
            for m in m1:
                if not m.isdigit() and m != "d":
                    match1 = False
            for m in m2:
                if not m.isdigit() and m != "d":
                    match2 = False
            if match1 and match2:
                m1 = [int(n) for n in m1 if n != "d"]
                m2 = [int(n) for n in m2 if n != "d"]
                if sum(m1) == 10 and sum(m2) == 10:
                    valid_formations.append(f)
                    unique_formations.add(f[1])
                    unique_formations.add(f[2])

                    if f[1] in unique_formations_dict:
                        unique_formations_dict[f[1]] += 1
                    else:
                        unique_formations_dict[f[1]] = 1

                    if f[2] in unique_formations_dict:
                        unique_formations_dict[f[2]] += 1
                    else:
                        unique_formations_dict[f[2]] = 1

                    # data_to_insert = (f[0], 'value2', 'value3')
                    cursor.execute("INSERT INTO formations (match_id, home_team_formation, away_team_formation) VALUES (?, ?, ?)", f)

                else:
                    partially_valid.append(f)
                    cursor.execute("INSERT INTO formations (match_id, home_team_formation, away_team_formation) VALUES (?, ?, ?)", (f[0], None, None))

            elif (match1 and not match2) or (match2 and not match1):
                partially_valid.append(f)
                cursor.execute("INSERT INTO formations (match_id, home_team_formation, away_team_formation) VALUES (?, ?, ?)", (f[0], None, None))


conn.commit()
conn.close()

print(len(valid_formations))
print(len(partially_valid))
print(len(list(unique_formations)))
print(valid_formations)
print(partially_valid)
print(list(unique_formations))

print(unique_formations_dict)
