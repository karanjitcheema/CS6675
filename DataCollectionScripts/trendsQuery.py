# Author: Tanay Amit Shah
# Date: April 16, 2012
# Project: Advanced Internet Computing Project
# Purporse: This module provides the queries for the web client

import globals
import json
import pycassa
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily
import traceback
import collections

# Creating the connection with Cassandra
cassandraIPPort = '10.253.76.221:9160'
pool = ConnectionPool('Keyspace1', [cassandraIPPort])
trends = pycassa.ColumnFamily(pool, 'TrendsColumnFamily')

def getTrend(word):
        getResult = trends.get(word)
        outputDict = collections.OrderedDict()
        keySet = getResult.keys()
        for key in keySet:
                time = key
                count = getResult[key]

                # Converting the time from MM:DD:HH to HH:DD:MM
                token = time.split(':')
                time = token[2] + ':' + token [1] + ':' + token[0]

                outputDict[time] = count

        # Return the JSON representation of the object
        returnJson = json.dumps(outputDict)
        return returnJson

def getTrends(words):
        returnList = []
        for word in words:
                jsonTrend = getTrend(word)
                returnList.append(jsonTrend)
        returnJson = json.dumps(returnList)
        return returnJson

