# server.py 
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

	print("Searching for new tags...")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))

	#data += clientsocket.recv(1024)#we only need to read once

	#end = data.find("NEW") #if the final end token is detected, break
	end = 0
	if end != -1:
		print("New tag found!")
		print("Writing to Socket...")
		name = "Dickling"
		w = clientsocket.send(name.encode("ascii"))
		if(w != -1):
			print("Write Successful")
		else:
			print("No Success")
	else:
		print("No new tag found") 
	clientsocket.close();