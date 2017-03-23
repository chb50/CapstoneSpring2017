# server.py 
import socket                                         
import time
import sys

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
while True: #accpeting loop
    # establish a connection
	print("loop around")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))
	while True: #reading loop
		data += clientsocket.recv(1024)#read once
		z = data.find("cedric") #detect starting token
		if z == -1:
			print("NO STARTING KEY FOUND")
			break
		data +=clientsocket.recv(1024)
		r =data.find("vineet")#detect ending token
		if r!= -1:
			print("ending key found halting now")
			clientsocket.send("halting reading process")
			break
	print("THE DATA FROM THE ARDUNIO IS %s" % data.decode('ascii'))
	clientsocket.close();
	break #remove for infite loop

