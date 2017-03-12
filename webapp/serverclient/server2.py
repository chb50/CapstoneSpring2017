# server.py 
import socket                                         
import time
import sys

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# universal name
host = '';                       

port = 9999                                           

# bind to the port
serversocket.bind((host, port))                                  

# queue up to 5 requests
serversocket.listen(5)                                           

data = ""
while True:
    # establish a connection
 clientsocket,addr = serversocket.accept()      
 print("Got a connection from %s" % str(addr))
#reading from socket
 data += clientsocket.recv(1024)
# assume the formating is something like smartgun code(not unqie)  smartgun id(unqie) assume the smart gun code is 6 characters
 data_end = data.find('\n') #loop reading until new line
 if data_end != -1:
	request = data[:data_end] #our full request
	if request.find('cedric',0,7) == -1: #cedric is our smartgun code in this case
		print("recived non smartgun request")
		clientsocket.close();
	else:
		clientsocket.send('Hello smart gun') #as vineet would say "good stuff",echo back to client
		print("smartgun found")
		clientsocket.close()