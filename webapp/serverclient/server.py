# server.py 

# IMPORTANT NOTE
# Make sure to allow access through firewall on a specific port
# when running this server on a windows machine


import socket                                         
import time

print("Running Connection")
	# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# universal name
host = '0.0.0.0';                       
port = 10000                                   
	# bind to the port
serversocket.bind((host, port))                                  
# queue up to 5 requests
serversocket.listen(5)                                           

data = ""

while True: #accepting loop

	print("Searching for Connection...")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))

	#data += clientsocket.recv(1024) #we only need to read once
	#end = data.find("NEW") #if the final end token is detected, break

	end = 0
	if end != -1:
		print("Writing to Socket...")
		name = "BOB"
		w = clientsocket.send(name)
		if(w != -1):
			print("Write Successful")
		else:
			print("No Success")
	else:
		print("No new tag found") 
	clientsocket.close();