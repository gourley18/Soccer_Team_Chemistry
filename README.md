# Soccer_Team_Chemistry
This project explores the relationship between player chemistry and match outcomes using machine learning models. Authored by Tyler Gourley in collaboration with Dr. Willie Harrison and the BYU ICE Lab.
#
#
# **FIRST TIME SETUP INSTRUCTIONS**
# To Set up the virtual environment:
#   1. Follow this tutorial:
#     https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
#     In Summary:
#       A. Create (and activate) a new virtual environment (you can choose the venv_name)
#            python -m venv <venv_name>
#          NOTE: This is how you activate your virtual environment on a Windows terminal: 
#            .\<venv_name>\Scripts\activate
#       B. Upgrade pip (while the virtual environment is activated)
#            python -m pip install --upgrade pip
#       C. Install packages into a virtual environment using the pip command
#          Remember to ensure the virtual environment is activated!
#            pip install -r 'requirements.txt'
# 
#   2. Add your virtual environment to the .gitignore
#     Add the following line under the virtual environments section of the .gitignore:
#           <venv_name>/
# 
# To Set up the database
#   1. Download the database from Box
#   2. Make sure the database is in the file location: db/lineups-data.db
#   3. Run the testDBConnection.py test script to ensure that a valid connection can be set up to the db
#   4. (Recommended) Download the SQLite Viewer extension on VSCode to easily interact with the database
#   5. Add the database to the .gitignore
#       - Make sure the following line of text is in the Database section of the .gitignore:
#           *.db
#

# Steps for the Future:
# 1. Finish compiling team chemistry data into .csv files (for years 2012-present)
#   - this is done by running hpc_data_compilation/compilation_final.py (For further details see README in hpc_data_compilation folder)

# 2. Dataset Improvements (For further details see README in data folder)
#   - alter the input data, X. One way to potentially improve the dataset is to put the opponents team chemistry data in the lower triangular portion of the array. This will help the machine learning models have more to train on. This should most likely be done by adjusting the already created .csv files instead of recompiling from the database. The polars package in python provides an easy-to-work-with interface to take in information from .csv and rearrange the data into numpy arrays or tensors.
#   - change the output data, y. One way to accomplish this is change the problem from a regression problem (numerical output) to a classification problem (probability over *n* number outcomes). In our case, we can adjust the output to 3 classes: WIN, LOSS, and TIE. These can be represented using one-hot encoding, where WIN: [1 0 0], TIE: [0 1 0], and LOSS: [0 0 1] (for example). The output would then be a vector of length 3 (be sure to apply softmax to the logit outputs so the values sum to 1.0). So, an output of [0.76, 0.21, 0.03] would mean that the model is predicting a 76% probabilistic chance that the true outcome of that match is a WIN.
#   - There is a possibility to use minutes played (instead of games played) as the metric for chemistry. This would require regenerating the .csv files from the database, and slightly adjusting the algorithm used to create it.

# 3. Experiment with other machine learning models
#   - LSTM neural network, CNN, a neural net Clustering Algorithm, SVM, GRU, and more!
#
#