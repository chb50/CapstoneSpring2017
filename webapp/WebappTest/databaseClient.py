# client.py  
import socket, time

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = "localhost" #vineets machine                           

port = 10000

print("Establishing Connection")
# connection to hostname on the port.
s.connect((host, port))                               

# Receive no more than 1024 bytes
print("Receiving Data")
tm = s.recv(1024)
print "Request Received"

time.sleep(2)

print "Sending DB"
s.send("SGD:\r\n1 Billy 123:543:23:8675\r\n")
print "Database information is sent"

print "Closing Connection" 
s.close()

print("Request Type: %s" % tm)
