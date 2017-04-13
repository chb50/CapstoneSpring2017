# client.py  
import socket

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

print("Closing Connection")
s.close()

print("Request Type: %s" % tm)
