# Author: Tanay Amit Shah
# Date: April 10, 2012
# Project: Advanced Internet Computing Project
# Purporse: Obtain tweets from the files generated with curl earlier and insert them into RabbitMQ's messaging queue
# Reference: http://www.arngarden.com/2012/11/07/consuming-twitters-streaming-api-using-python-and-curl/

#!/usr/bin/python

import os
import pika
import sys

# The folder from where all (and only) the raw data files are placed
# Place only one copy of the file and don't place any other random files in this folder
RAW_DATA_FOLDER = '/home/tanay/Desktop/AIC.Project/RawDataFiles/'

# Setting up the RabbitMQ producer connection using the pika client library
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='tweetsQueue', durable=True)

# Maintain a list of the new files created
# These will be deleted at the end of the program
newFilesCreated = []

# Obtain all the file names from the RAW_DATA_FOLDER
files = os.listdir(RAW_DATA_FOLDER)
for file in files:
	path = RAW_DATA_FOLDER + file
	command = 'head -n -1 ' + path + '>' + path + 'temp'
	os.system(command)
	newFilesCreated.append(path + 'temp')
	with open(path + 'temp', 'r') as f:
		for line in f:
			channel.basic_publish(exchange='',
				routing_key='tweetsQueue',
				body=line,
				properties=pika.BasicProperties(delivery_mode=2))
	

for file in newFilesCreated:
	os.system('rm ' + file)		
connection.close()
		
