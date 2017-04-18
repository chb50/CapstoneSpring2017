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
print "Receiving Data"
tm = s.recv(1024)
print "Request Received ", tm
name = tm

print "Registering name"
time.sleep(1)

s.send("NAME_GET")
# waiting for new data
s.close()
time.sleep(10)

print "Establishing new connection"
# connection to hostname on the port.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.connect((host, port))  

tm = s.recv(1024)

print "Name = ", name

print "Sending DB"
s.send("SGD:\r\n1 %s 123:543:23:8675\r\n" % name)
print "Database information is sent"

print "Closing Connection" 
s.close()

