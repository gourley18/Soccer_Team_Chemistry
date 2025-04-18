# hpc_data_compilation
Various files that were created to benchmark performance of data compilation.

compilation_final.py -
  **MOST UPDATED VERSION**
  starting at line 143, there are 3 variables that you can set:
  NUM_MATCHES = None # Select NONE to not limit query (50 means that it will only return the first 50 results from that year)
  YEAR = 2011 # set the YEAR variable to the year you want to get the data for
  NUM_PROCS = multiprocessing.cpu_count() # This sets the number of processors to the number on your computer
  
  It will save a .csv file with the Team Chemistry data

compilation_parallel.py - 
  V2 of parallel implementation, for benchmarking purposes
compilation_serial.py - 
  serial implementation, for benchmarking purposes
compilation_unoptimized.py - 
  V1 of parallel implementation, for benchmarking purposes
  
Database.py -
  Class that manages access to the database
  instance of this class is invoked by each of the python files above.
