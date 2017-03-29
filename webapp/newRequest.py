from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL
import socket                                         
import time

app = Flask(__name__)

# 1) Open a new page that will take in input that a new tag needs to be registered
# 2) In the input field, input the name to be associated with the new tag and press "add new tag button"
# 3) Will send the request "N'name'"
# 4) Will receive confirmation from the client that tag had been registered or not
# 5) Notify user of the registration status

@app.route("/")
def main():

	request = runConnection()

	return render_template("request.html", request=request)


def runConnection():
	print("Running Connection")
	name = "CuckWad" #make sure to append the termination character
	request = "N" + name
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

		clientsocket.send(request)

		data += clientsocket.recv(1024)#we only need to read once

		end = data.find("NEW") #if the final end token is detected, break
		if end != -1:
			print("New Tag Registered")
			clientsocket.close()
			serversocket.close()
			return True
		else:
			print("Error in Registration")
			clientsocket.close()
			serversocket.close() 
			return False

	

if __name__ == "__main__":
	app.run(debug = True)