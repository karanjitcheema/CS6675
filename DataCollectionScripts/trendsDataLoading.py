# Author: Tanay Amit Shah
# Date: April 12, 2012
# Project: Advanced Internet Computing Project
# Purporse: This module inputs the trends data into cassandra

import os
import sys
import globals
import json
import pycassa
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
import traceback


# Creating the connection with Cassandra
cassandraIPPort = '10.253.76.221:9160'
pool = ConnectionPool('Keyspace1', [cassandraIPPort])
trends = pycassa.ColumnFamily(pool, 'TrendsColumnFamily')

print '**************************************'
print 'Loading trends data into Cassandra'

# Get the most recent MapReduce output directory
listOfMapReduceOutputDir = os.listdir(globals.OUTPUT_DIR)
listOfMapReduceOutputDir.sort()
OutputDirectory = listOfMapReduceOutputDir[-1]

count = 0

# Process the files that corresponds to the latest MapReduce output directory
listOfMapReduceFiles = os.listdir(globals.OUTPUT_DIR + "/" + OutputDirectory)
for file in listOfMapReduceFiles:
        filePath = globals.OUTPUT_DIR + "/" + OutputDirectory + "/" + file
        with open(filePath, 'r') as f:
                for line in f:
                        try:
                                outputJson = json.loads(line)
                                trends.insert(outputJson['word'], {outputJson['time']: int(outputJson['count'])})
                                count+=1
                                print count
                        except:
                                print 'Error in processing ' + line
                                traceback.print_exc()









