from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL
import socket                                         
import time
import datetime

#In the database make the date and time a char of length 10

#authenticate the user with mysql 
#mysql = MySQL()
app = Flask(__name__)
#app.config['MYSQL_HOST'] = '172.27.163.117'
#app.config['MYSQL_USER'] = 'stone'
#app.config['MYSQL_PASSWORD'] = 'password'
#app.config['MYSQL_DB'] = 'testmcu'
#mysql.init_app(app)


@app.route("/")
def main():

	results = connection()

	table = [] 

	for i in range(0,len(results)):
		table.append(results[i])

	for i in range(len(results)-1, 11):
		table.append(" ")
	print table

	return render_template("database.html", table=table, length=len(results))



def connection():
	print("Running connection")
		# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

	# universal name
	host = '0.0.0.0';                       
	port = 10001                                       

	# bind to the port
	serversocket.bind((host, port))                                  

	# queue up to 5 requests
	serversocket.listen(5)                                           

	data = ""
	i = 0
	table = []

	request = "D"

	while True: #accpeting loop
	    # establish a connection
		print("Waiting for connection...")
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))

		clientsocket.send(request)

		while True: #reading loop
			data += clientsocket.recv(1024)#read once

			if i == 0: #if it is the first read, check for correct starting token
				z = data.find("SGD:") #detect starting token
				if z == -1: #if no starting token found, break connection
					print("NO STARTING KEY FOUND")
					break

			end = data.find("SGD:END") #if the final end token is detected, break
			if end != -1:
				clientsocket.close();
				return table

			r = data.find("\r\n")#detect ending line token
			if r != -1:# if ending line token is detected
				i = i+1 # increment index
				table.append(data) # add the data to the table
				data = "" # empty the data buffer
	clientsocket.close();


if __name__ == "__main__":
	app.run(debug = True)