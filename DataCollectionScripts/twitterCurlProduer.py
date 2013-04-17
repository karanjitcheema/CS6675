# Author: Tanay Amit Shah
# Date: April 10, 2012
# Project: Advanced Internet Computing Project
# Purporse: Obtain tweets from Twitter's streaming API and insert them into RabbitMQ's messaging queue
# Reference: http://www.arngarden.com/2012/11/07/consuming-twitters-streaming-api-using-python-and-curl/

#!/usr/bin/python

import time
import pycurl
import urllib
import json
import oauth2 as oauth
import os
import pika
import sys

# The PID that will be sent to the consumer so that they can kill this process if something goes wrong
PID = str(os.getpid())

STREAMING_API_URL = 'https://stream.twitter.com/1.1/statuses/filter.json'

# This can actually be anything
USER_AGENT = 'AIC.PROJECT' 

# Using the OAUTH_KEYS that were generated for the application that belongs to tanayamitshah@gmail.com 
OAUTH_KEYS = {'consumer_key': 'NDasSgq4rLwaWKL4GYtTqg',
              'consumer_secret': 'vPrf2di7kvE6sGBGAB4aCT7Y5KtaSTeNCfZrk575g',
              'access_token_key': '380720332-5dnJtsjJ7z6d9AhL7jwWgapTefc0PU46vrYlje1p',
              'access_token_secret': 'fzudCMfWAsiovdbFbADSfdYdGU503Xj2ZJd5laYdY'}

# These values are posted when setting up the connection
# Don't need to URL encode the track keywords because we do that in code when setting up the connection
POST_PARAMS = {'include_entities': 1,
               'stall_warning': 'true',
               'track': 'arsenal,afc,chelsea,cfc,liverpool,lfc,tottenham,thfc,machesterunited,manchester united,mufc,manchestercity,manchester city,mancity'}


# Setting up the RabbitMQ producer connection using the pika client library
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='tweetsQueue', durable=True)

class TwitterStream:
	# The constructor for the TwitterStream class
	# Sets up the member variables using the global variables earlier
	# By default the timeout is not set. Set it to an integer to initialize it
	def __init__(self, timeout=False):
		self.oauth_token = oauth.Token(key=OAUTH_KEYS['access_token_key'], secret=OAUTH_KEYS['access_token_secret'])
		self.oauth_consumer = oauth.Consumer(key=OAUTH_KEYS['consumer_key'], secret=OAUTH_KEYS['consumer_secret'])
		self.conn = None
		self.buffer = ''
		self.timeout = timeout
		self.setup_connection()
		self.count = 0

	
	def setup_connection(self):
		# If we already have a connection then close it and empty the buffer used to store temporary data
		if self.conn:
			self.conn.close()
			self.buffer = ''

		# Setting up the necessary curl parameters
		self.conn = pycurl.Curl()

		# Restart connection if less than 1 byte/s is received during timeout seconds
		# In order to enable the timeout have to specify a timeout integer value
		if isinstance(self.timeout, int):
			self.conn.setopt(pycurl.LOW_SPEED_LIMIT, 1)
			self.conn.setopt(pycurl.LOW_SPEED_TIME, self.timeout)

		# Setting up the URL and Useragent parameters of curl using the global variables specified earlier
		self.conn.setopt(pycurl.URL, STREAMING_API_URL)
		self.conn.setopt(pycurl.USERAGENT, USER_AGENT)

		# Using gzip is optional but saves us bandwidth.
		self.conn.setopt(pycurl.ENCODING, 'deflate, gzip')

		# Specifying that the request is a POST request as well as the POST parameters
		self.conn.setopt(pycurl.POST, 1)
		self.conn.setopt(pycurl.POSTFIELDS, urllib.urlencode(POST_PARAMS))

		# Host is needed so that we getting gzipped stream and the Authorization corresponds to the OAuth authentication
		self.conn.setopt(pycurl.HTTPHEADER, ['Host: stream.twitter.com', 'Authorization: %s' % self.get_oauth_header()])

		# handle_tweet is the callback for when new tweets are received
		self.conn.setopt(pycurl.WRITEFUNCTION, self.handle_tweet)


	# Creates and returns the OAuth header
	def get_oauth_header(self):
		params = {'oauth_version': '1.0',
			'oauth_nonce': oauth.generate_nonce(),
			'oauth_timestamp': int(time.time())}
		req = oauth.Request(method='POST', parameters=params, url='%s?%s' % (STREAMING_API_URL, urllib.urlencode(POST_PARAMS)))
		req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self.oauth_consumer, self.oauth_token)
		return req.to_header()['Authorization'].encode('utf-8')


	# Start listening to Streaming endpoint and handle exceptions according to Twitter's recommendation
	# Handle network error, HTTP errors and HTTP 420 error 
	# https://dev.twitter.com/docs/streaming-apis/connecting#Reconnecting
	def start(self):
		backoff_network_error = 0.25
		backoff_http_error = 5
		backoff_rate_limit = 60
		while True:
			# Setup the connection first
			self.setup_connection()
			try:
				# Go into an infinite loop that receives the tweet and calls the callback
				self.conn.perform()
			except:
				# Network error, use linear back off up to 16 seconds 
				print 'Network error: %s' % self.conn.errstr()
				print 'Waiting %s seconds before trying again' % backoff_network_error
				time.sleep(backoff_network_error)
				backoff_network_error = min(backoff_network_error + 1, 16)
				continue
			# HTTP Error
			sc = self.conn.getinfo(pycurl.HTTP_CODE)
			if sc == 420:
				# Rate limit, use exponential back off starting with 1 minute and double each attempt
				print 'Rate limit, waiting %s seconds' % backoff_rate_limit
				time.sleep(backoff_rate_limit)
				backoff_rate_limit *= 2
			else:
				# HTTP error, use exponential back off up to 320 seconds
				print 'HTTP error %s, %s' % (sc, self.conn.errstr())
				print 'Waiting %s seconds' % backoff_http_error
				time.sleep(backoff_http_error)
				backoff_http_error = min(backoff_http_error * 2, 320)

	# The Callback for the tweets
	def handle_tweet(self, data):
		self.buffer += data
		if data.endswith('\r\n') and self.buffer.strip():
			# Complete message received so publish it to the queue
			# Publish the content of self.buffer 
			# The delivery mode is set to make the message persistent
			self.count+=1
			channel.basic_publish(exchange='', 
				routing_key='tweetsQueue', 
				body=self.buffer, 
				properties=pika.BasicProperties(delivery_mode=2))
			self.buffer = ''			
			if self.count%50 == 0:
				print 'Recvd 50 ' + time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
				self.count = 0

# The main class of the entire script
if __name__ == '__main__':
    ts = TwitterStream()
    ts.setup_connection()
    ts.start()
