# server.py 
import socket                                         
import time
import sys
import datetime

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# universal name
host = '0.0.0.0';                       
z = -1
port = 10000                                           

# bind to the port
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)                                           

data = ""
while True: #accpeting loop
    # establish a connection
	print("Waiting for connection...")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))
	first = datetime.datetime.now()
	while True: #reading loop
		now = datetime.datetime.now()
		if( (now.second - first.second) >= 10):
			break
		data += clientsocket.recv(1024)#read once
		z = data.find("SGD:") #detect starting token
		if z == -1:
			print("NO STARTING KEY FOUND")
			break
		data +=clientsocket.recv(1024)
		r = data.find("\r\n\r\n")#detect ending token
		if r != -1:#if ending token is detected
			break
	print("-----------Arduino Data-----------\n%s" % data.decode('ascii'))

clientsocket.close();

