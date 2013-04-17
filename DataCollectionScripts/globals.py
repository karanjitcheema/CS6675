# Author: Tanay Amit Shah
# Date: April 12, 2012
# Project: Advanced Internet Computing Project
# Purporse: This module contains global variables that point to the important directories of the project. 

#!/usr/bin/python

# The home directory of MapReduce
MAPREDUCE_HOME = "/home/tanay/Desktop/hadoop-1.0.4"
# The temporary directory to be used to load data into HDFS
HDFS_INPUT_TEMP = MAPREDUCE_HOME + "/input"
# The temporary directory to be used to get data out of HDFS
HDFS_OUTPUT_TEMP = MAPREDUCE_HOME + "/output"
# The directory in HDFS to load the data to 
HDFS_INPUT = "/user/tanay/input"
# The directory in HDFS to store the output data to
HDFS_OUTPUT = "/user/tanay/output"



# The home directory of the AIC project
PROJECT_HOME = "/home/tanay/Desktop/AIC.Project"
# The directory that contains all the python scripts
SCRIPTS_HOME = PROJECT_HOME + "/DataCollectionScripts"
# The directory that contains the output of the preprocessing scripts
PROCESSED_DIR = PROJECT_HOME + "/ProcessedData"
# The directory that contains the older output of the preprocessing scripts
ARCHIVED_PROCESSED_DIR = PROJECT_HOME + "/ArchivedProcessedData"
# The output of the MapReduce code should go into this folder
OUTPUT_DIR = PROJECT_HOME + "/MapReduceOutput"
# The output of the Indexing code should go into this folder
OUTPUT_INDEX_DIR = PROJECT_HOME + "/MapReduceIndexOutput"
