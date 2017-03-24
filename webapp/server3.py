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
port = 9999                                           

# bind to the port
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)                                           

data = ""
i = 0
table = []
while True: #accpeting loop
    # establish a connection
	print("Waiting for connection...")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))
	while True: #reading loop
		data += clientsocket.recv(1024)#read once

		if i == 0: #if it is the first read, check for correct starting token
			z = data.find("SGD:") #detect starting token
			if z == -1: #if no starting token found, break connection
				print("NO STARTING KEY FOUND")
				break

		end = data.find("SGD:END") #if the final end token is detected, break
		if end != -1:
			break

		r = data.find("\r\n")#detect ending line token
		if r != -1:# if ending line token is detected
			i = i+1 # increment index
			table.append(data) # add the data to the table
			data = "" # empty the data buffer

	#print out the data received from the arduino
	print("-----------Arduino Data-----------")
	for index in range(0, i):
		print(table[index].decode('ascii'))
	

clientsocket.close();

