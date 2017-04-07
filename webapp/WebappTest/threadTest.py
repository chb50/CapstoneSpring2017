from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL
import socket, time
import threading

app = Flask(__name__)

HOST = '0.0.0.0'
PORT = 17078

exitFlag = 0
request = None

class ThreadedServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        while True:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                self.sock.bind((HOST, PORT))
                self.sock.listen(5)
            except socket.error as msg:
                print "We are in bind loop"
                self.sock.close()
                self.sock = None
                continue
            break
        

    def run(self):
        print "Starting Socket Thread"

        global request
        request = "D"
        
        while True:
            print "Waiting for new request"
            while True:
                if(request != None):
                    break
                print request
                time.sleep(0.25)

            print "Request Received\nWaiting for Connection..."
            client, address = self.sock.accept()
            print("Got a connection from %s" % str(address))
            client.settimeout(60)

            client.send(request)
            print "Request sent"
            request = None

            client.close()


# Couple of random routes to check for different request types
@app.route("/request", methods=['POST','GET'])
def request():
    global request
    request = "NParallelBob"
    print "request = ", request
    return render_template("request.html")

@app.route("/SGID", methods=['POST','GET'])
def SGID():
    global request
    request = 'O'
    print "request = ", request
    return render_template("otk.html")

@app.route("/database", methods=['POST','GET'])
def database():
    global request
    request = 'D'
    print "request = ", request
    return render_template("databaseParallel.html")

@app.route("/", methods=['POST','GET'])
def main():
    global request
    request = None
    return render_template("mainPage.html")
 

if __name__ == "__main__": 

    socketThread = ThreadedServer()
    socketThread.start()

    print "Now Running Main"
    app.run(debug = True)