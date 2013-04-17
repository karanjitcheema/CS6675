# Author: Tanay Amit Shah
# Date: April 10, 2012
# Project: Advanced Internet Computing Project
# Purpose: The consumer of the RabbitMQ queue. Responsible for preprocessing the tweets and creating the input to the Hadoop file

import os
import pika
import json
import string
from bs4 import BeautifulSoup
import time
import globals
import traceback

# Used for debugging and for creating new files
countUnit = 0
countThousand = 0

def generateFileName():
	timeString = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
	return globals.PROCESSED_DIR + '/'  + 'file-'+timeString+'.txt'

# Setting up the connection with RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='tweetsQueue', durable=True)

currentFile = open(generateFileName(), 'a'); 

def incrementCounters():
	global countUnit
	global countThousand
	global currentFile
	countUnit += 1
	if countUnit%500 == 0:
		print str(countThousand*1000+countUnit) + ' ' + \
			time.strftime("%H:%M:%S", time.gmtime())
	if countUnit == 1000:
		countThousand+=1
		countUnit = 0
		# Create a new file when you write 
		if countThousand%10 == 0:
			currentFile.close()
			currentFile = open(generateFileName(),'a');			      
		# For every 10th file, run the MapReduce job in the bacground
		if countThousand%100 == 0:
			command = ('python ' + globals.SCRIPTS_HOME + '/MapReduceController.py &')		
			print command
#			os.system(command)
			
# This function will process each tweet record which can be an error or a tweet
# Can use this along with the Message queue as well as along with the precollected data
def processTweetRecord(record):
	# Read the JSON object first
	try:
		tweetJson = json.loads(record)

		# Check if we got rate limited, disconnected or a warning
		# TODO: Write code to take care of these circumstances
		if tweetJson.get('limit'):
        		print 'Rate limiting caused us to miss %s tweets' % (tweetJson['limit'].get('track'))
		elif tweetJson.get('disconnect'):
        		print ('Got disconnect: %s' % tweetJson['disconnect'].get('reason'))
	        elif tweetJson.get('warning'):
        	        print 'Got warning: %s' % tweetJson['warning'].get('message')
	        elif tweetJson.get('text'):
			incrementCounters()
			# Isolating all the values that we care about from the tweets
			created_at = tweetJson.get('created_at')
			id_str = tweetJson.get('id_str')
			lang = tweetJson.get('lang')
			text = tweetJson.get('text')
			user = tweetJson.get('user').get('screen_name')
			user_id_str = tweetJson.get('user').get('id_str')

			# Reformatting the time string
			parsedTime = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
			created_at = str(parsedTime.tm_year) + ':' + \
				str(parsedTime.tm_mon).zfill(2) + ':' + \
				str(parsedTime.tm_mday).zfill(2) + ':' + \
				str(parsedTime.tm_hour).zfill(2) + ':' + \
				str(parsedTime.tm_min).zfill(2) + ':' + \
				str(parsedTime.tm_sec).zfill(2)

			# Removing urls from the text
			rawUrls = tweetJson.get('entities').get('urls')
			for url in reversed(rawUrls):
				startIndex = url.get('indices')[0]
				endIndex = url.get('indices')[1]
				textPart1 = text[:startIndex]
				textPart2 = text[endIndex:]
				text = textPart1 + textPart2
			
			# Cleaning the text	
			soup = BeautifulSoup(text)
			text = soup.get_text().replace(u"\xa0", " ")
			text = text.encode("ascii","ignore")
			text = text.translate(string.maketrans("",""), string.punctuation)
			text = text.replace("\n", " ").replace("\r", " ").strip()
			text = text.lower()

			# Removing extra spaces from the text
			textArray = text.split()
			text = ''
			for word in textArray: 
				text = text + word + ' '
	
			# Processing the hashtags 
			rawHashtags = tweetJson.get('entities').get('hashtags')
			hashtags = []
			for hashtag in rawHashtags:
				soup = BeautifulSoup(hashtag.get('text'))
				temp = soup.get_text().replace(u"\xa0", " ")
				temp = temp.encode("ascii","ignore")
				temp = temp.translate(string.maketrans("",""), string.punctuation)
				temp = temp.replace("\n", " ").replace("\r", " ").strip()
				temp = temp.lower()
				hashtags.append(temp)

			# Creating a dict of these values
			processedTweetDict = {}
			processedTweetDict['created_at'] = created_at
			processedTweetDict['id_str'] = id_str
			processedTweetDict['lang'] = lang
			processedTweetDict['text'] = text
			processedTweetDict['user'] = user
			processedTweetDict ['user_id'] = user_id_str
			processedTweetDict['hashtags'] = hashtags
		
			outputJson = json.dumps(processedTweetDict)
			currentFile.write(outputJson+'\n')	
	except:
		print 'Error processing ' + record
		traceback.print_exc()

# The callback for each message that is received from the producer
# The message received can be a tweet or an error
# If it is a tweet then we will process it. If it is an error then we will display to stdout
def callback(ch, method, properties, body):
	processTweetRecord(body)	

# Start reading from the stream
channel.basic_consume(callback, queue='tweetsQueue', no_ack=True)
channel.start_consuming()
