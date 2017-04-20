from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL
import socket, time
import threading

app = Flask(__name__)


@app.route("/")
def main():

	request = runConnection()

	return render_template("request.html", request=request)


def runConnection():

	print("Running Connection")
	name = "dickling" #make sure to append the termination character
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

	# socketThread = new_thread(1, "Socket Thread")
	app.run(debug = True)