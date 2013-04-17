A.) twitterCurl.py
	Requirements:
		1.) pycurl
			apt-cache depends python-pycurl   
			sudo apt-get install libcurl4-gnutls-dev
			pip install pycurl
		2.) oauth2
			sudo pip install oauth2

B.) RabbitMQ
	Install:
		Add to /etc/apt/sources.list: deb http://www.rabbitmq.com/debian/ testing main
		wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
		sudo apt-key add rabbitmq-signing-key-public.asc
		sudo apt-get update
		sudo apt-get install rabbitmq-server
		sudo pip install pika==0.9.8

	Starting and Stopping:
		The RabbitMQ Server runs by default as a daemon when installed. It is run under the user rabbitmq
		Starting RabbitMQ Server: invoke-rc.d rabbitmq-server start
		Stopping RabbitMQ Server: invoke-rc.d rabbitmq-server stop
		
	Managing RabbitMQ: (http://www.rabbitmq.com/man/rabbitmqctl.1.man.html)
		sudo rabbitmqctl
		To stop the server: sudo rabbitmqctl stop 
		To check status of server: sudo rabbitmqctl status
		To list the queues: sudo rabbitmqctl list_queues

C.) twitterConsumer.py
	Requirements:
		1.) Beautiful soup
			pip install beautifulsoup4


D.) Follow the steps in EC2 installation file

E.) Follow the Instuctions in MapReduce Commands to initate map reduce



