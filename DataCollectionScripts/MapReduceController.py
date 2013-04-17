# Author: Tanay Amit Shah
# Date: April 12, 2012
# Project: Advanced Internet Computing Project
# Purporse: Performs the MapReduce jobs on the recently collected data
# Assumption: Hadoop is already running and stable

#!/usr/bin/python

import os
import sys
import globals
from time import gmtime, strftime

timestamp = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

print '********************************'
print 'Started the MapReduce Controller at ' + timestamp


# Format the input and the output directories of HDFS
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop fs -rmr " + globals.HDFS_INPUT);
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop fs -rmr " + globals.HDFS_OUTPUT);


# Format the input and the output directories in MAPREDUCE_HOME
os.system("rm -r " + globals.HDFS_INPUT_TEMP + "/*");
os.system("rm -r " + globals.HDFS_OUTPUT_TEMP);


# Copy all the most recent completed files
# Moving from the ProcessedData directory to the HDFS input directory
# Also copy the data to the archive directory
# We deal with all but the last file since the last file as it is active
listOfRecentFiles = os.listdir(globals.PROCESSED_DIR)
listOfRecentFiles.sort()
del listOfRecentFiles[-1]

if len(listOfRecentFiles) < 3:
	sys.exit()

for file in listOfRecentFiles:
	filePath = globals.PROCESSED_DIR + "/" + file

	# Copy the file to archive directory
	os.system("cp " + filePath + " " + globals.ARCHIVED_PROCESSED_DIR)
	# Move the file to the Hadoop directory
	os.system("mv " + filePath + " " + globals.HDFS_INPUT_TEMP)

print 'Copied and Moved the files to the archive and input folders'

# Load the data into HDFS
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop fs -put " + \
		globals.HDFS_INPUT_TEMP + " " + globals.HDFS_INPUT);

# Run the trends MapReduce job and get the output
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop jar " + globals.MAPREDUCE_HOME + "/tweetstrends.jar org.aic.MapReduceTrends " + \
	globals.HDFS_INPUT + " " + globals.HDFS_OUTPUT)
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop fs -get " + globals.HDFS_OUTPUT + \
	" " + globals.HDFS_OUTPUT_TEMP)


# Copy the output files to the MapReduceOutput directory in the project
newFolderName = 'output-' + timestamp
newFolderPath = globals.OUTPUT_DIR + "/" + newFolderName
os.system("mkdir " + newFolderPath)
os.system("mv " + globals.HDFS_OUTPUT_TEMP + "/part-* " + newFolderPath) 

# Not running the index job as it is too large
'''
# Repreparing for running the index job
os.system("rm -r " + globals.HDFS_OUTPUT_TEMP);
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop fs -rmr " + globals.HDFS_OUTPUT);

# Running the index job
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop jar " + globals.MAPREDUCE_HOME + "/tweetsindex.jar org.aic.MapReduceIndex " + \
	globals.HDFS_INPUT + " " + globals.HDFS_OUTPUT)
os.system(globals.MAPREDUCE_HOME + "/bin/hadoop fs -get " + globals.HDFS_OUTPUT + \
	" " + globals.HDFS_OUTPUT_TEMP)

# Copy the output files to the MapReduceOutput directory in the project
newFolderName = 'output-' + timestamp
newFolderPath = globals.OUTPUT_INDEX_DIR + "/" + newFolderName
os.system("mkdir " + newFolderPath)
os.system("mv " + globals.HDFS_OUTPUT_TEMP + "/part-* " + newFolderPath) 
'''

timestamp = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
print 'MapReduceController job finished at ' +  timestamp
print '********************************'

