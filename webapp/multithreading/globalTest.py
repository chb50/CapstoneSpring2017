#!/usr/bin/python

import threading
import time, sys
import socket

HOST = '0.0.0.0'
PORT = 10000

exitFlag = 0

request = None

class ThreadedServer(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def run(self):
        print "Starting Socket Thread"

        self.sock.listen(5)

        global request
        request = None
        
        while True:
            print "Waiting for new request"
            while True:
                if(request != None):
                    break
                time.sleep(0.25)

            print "Request Received\nWaiting for Connection..."
            client, address = self.sock.accept()
            print("Got a connection from %s" % str(address))
            client.settimeout(60)

            client.send(request)
            print "Request sent"
            request = None

            client.close()


class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print "Starting " + self.name
        print_time(self.name, self.counter)
        print "Exiting " + self.name



class newThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print "Starting " + self.name
        wait_time(self.name)
        print "Exiting " + self.name



#functions 
def print_time(threadName, delay):
    while True:
        if request == "O":
            print "Thread 1 Request is now =", request
            break
        time.sleep(delay)
        print "%s: %s" % (threadName, time.ctime(time.time()))

def wait_time(threadName):
    while True:
        if(request != None):
            print "Thread 2 request is now", request
            break
        print request
        time.sleep(0.25)

if __name__ == "__main__":
    serverThread = ThreadedServer(HOST,PORT)
    serverThread.start()

    # Create new threads
    thread1 = myThread(1, "Thread-1", 1)
    thread2 = newThread(2, "Thread-2")

    # Start new Threads
    thread1.start()
    thread2.start()

    time.sleep(5)
    request = "O"

    print ("Exiting Main Thread")



