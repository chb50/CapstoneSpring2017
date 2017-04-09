from flask import Flask, render_template
import os, sys, socket
import socket, time
import threading

app = Flask(__name__)
	
# universal name
host = '0.0.0.0';                       
port = 10000                           

request = None
#Prototype of the threaded version is now working

# class for threads
class new_thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        runConnection(self.name)
        print "Exiting " + self.name


# This is what the thread is running in parallel with the program
def runConnection(threadName):
	print "-" * 15
	print("Running Connection")
	print "-" * 15
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# try:
	# 	serversocket.bind((host, port))                                  
	# except socket.error as msg:
	# 	serversocket.bind((host, port+1))                                  


	serversocket.bind((host, port))                                  
	serversocket.listen(5) 

	global request
	request = None

	print "Waiting for request"
	while True: #accepting loop
		while True:
			if(request != None):
				print "Received a Request!!!"
				break
			time.sleep(0.25)
			
		print "----------------------------------------"
		print request
		print "----------------------------------------"
		print("Searching for Connection...")
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))

		clientsocket.send(request)
		request = None

		clientsocket.close()
	serversocket.close()


#Just two random routes to check if the program can swtich between them while running the server
@app.route("/request", methods=['POST','GET'])
def request():
	global request
	request = "NParallelBob"
	return render_template("request.html")

@app.route("/SGID", methods=['POST','GET'])
def SGID():
	global request
	request = "O"
	return render_template("otk.html")

@app.route("/database", methods=['POST','GET'])
def database():
	global request
	request = "D"
	return render_template("databaseParallel.html")

@app.route("/", methods=['POST','GET'])
def main():
	global request 
	request = None
	return render_template("mainPage.html")
 


if __name__ == "__main__":                                       

	socketThread = new_thread(1, "Socket Thread")
	socketThread.start()

	app.run()