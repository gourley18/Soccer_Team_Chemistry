# The files in this folder hold the outputs of the compilation of Team Chemistry Data (found in the hpc_data_compilation folder)
# These are .csv formats that contain chemistry data for the given team (features 1-55), and match outcome (goals scored and goals allowed)
# There are 2 rows for every match (one for each team)
#
# IMPORTANT: To produce more .csv files like these, you should run the python script located here:
#   hpc_data_compilation/compilation_final.py
#
# These features populate an upper triangular array (not including the diagonal) as shown below

|     | P1  | P2  | P3  | P4  | P5  | P6  | P7  | P8  | P9  | P10 | P11 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| P1  |  -  | F1  | F2  | F3  | F4  | F5  | F6  | F7  | F8  | F9  | F10 |
| P2  |     |  -  | F11 | F12 | F13 | F14 | F15 | F16 | F17 | F18 | F19 |
| P3  |     |     |  -  | F20 | F21 | F22 | F23 | F24 | F25 | F26 | F27 |
| P4  |     |     |     |  -  | F28 | F29 | F30 | F31 | F32 | F33 | F34 |
| P5  |     |     |     |     |  -  | F35 | F36 | F37 | F38 | F39 | F40 |
| P6  |     |     |     |     |     |  -  | F41 | F42 | F43 | F44 | F45 |
| P7  |     |     |     |     |     |     |  -  | F46 | F47 | F48 | F49 |
| P8  |     |     |     |     |     |     |     |  -  | F50 | F51 | F52 |
| P9  |     |     |     |     |     |     |     |     |  -  | F53 | F54 |
| P10 |     |     |     |     |     |     |     |     |     |  -  | F55 |
| P11 |     |     |     |     |     |     |     |     |     |     |  -  |

# feature_1 (F1) represents number of games played prior to this game (contained in the database) in common between Player 1 (P1) and Player 2 (P2)
# feature_2 represents number of games played in common between Player 1 and Player 3
# feature_3 represents number of games played in common between Player 1 and Player 4
# ...
# feature_11 represents number of games played in common between Player 2 and Player 3
# ...
# feature_53 represents number of games played in common between Player 9 and Player 10
# feature_54 represents number of games played in common between Player 9 and Player 11
# feature_55 represents number of games played in common between Player 10 and Player 11
#
# 
# Future Dataset Improvements:
#   - one way to potentially improve the dataset is to put the opponents team chemistry data in the lower triangular portion of the array. This will help the machine learning models have more to train on. This should most likely be done by adjusting the already created .csv files instead of recompiling from the database. The polars package in python provides an easy-to-work-with interface to take in information from .csv and rearrange the data into numpy arrays or tensors
#   - There is a possibility to use minutes played (instead of games played) as the metric for chemistry. This would require regenerating the .csv files from the database, and slightly adjusting the algorithm used to create it.

