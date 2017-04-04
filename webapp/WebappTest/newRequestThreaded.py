from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL
import socket, time
import threading

app = Flask(__name__)
	
# universal name
host = '0.0.0.0';                       
port = 10000                              


#class for threads
class new_thread (threading.Thread):
    def __init__(self, threadID, name, ssocket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.serversocket = ssocket
    def run(self):
        print "Starting " + self.name
        runConnection(self.name, self.serversocket)
        print "Exiting " + self.name


#This is what needs to be running while the webapp is running
def runConnection(threadName, serversocket):
	name = "bob"
	request = "N" + name

	while True: #accepting loop

		print("Searching for Connection...")
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))

		clientsocket.send(request)

		clientsocket.close()
	serversocket.close()


@app.route("/request", methods=['POST','GET'])
def request():
	return render_template("request.html", request=request)

@app.route("/", methods=['POST','GET'])
def main():
	return render_template("mainPage.html", request=request)



if __name__ == "__main__":

	print("Running Connection")
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversocket.bind((host, port))                                  
	serversocket.listen(5)                                           

	# socketThread = new_thread(1, "Socket Thread", serversocket)
	# socketThread.start()
	app.run(debug = True)