# To Set up the database
#   1. Download the database from Box
#   2. Make sure the database is in the file location: db/lineups-data.db
#   3. Run the testing_scripts/testDBConnection.py test script to ensure that a valid connection can be set up to the db
#        - You may need to adjust the relative path to the database (currently line 17)
#   4. (Recommended) Download the SQLite Viewer extension on VSCode to easily interact with the database
#   5. Add the database file to the .gitignore
#       - Make sure the following line of text is in the Database section of the .gitignore:
#           *.db