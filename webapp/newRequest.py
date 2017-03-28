from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL
import socket                                         
import time

app = Flask(__name__)


@app.route("/")
def main():

	request = runConnection()

	return render_template("request.html", request=request)


def runConnection():
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

		data += clientsocket.recv(1024)#we only need to read once

		end = data.find("NEW") #if the final end token is detected, break
		if end != -1:
			print("New tag found!")
			print("Writing to Socket...")
			name = "Richard" #make sure to append the termination character
			w = clientsocket.send(name)
			if(w != -1):
				print("Write Successful")
			clientsocket.close();
			return True
		else:
			print("No new tag found")
			clientsocket.close(); 
			return False

	

if __name__ == "__main__":
	app.run(debug = True)