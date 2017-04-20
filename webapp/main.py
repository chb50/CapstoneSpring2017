from flask import Flask, render_template, request, redirect, url_for
from flask import session, flash
from flask import jsonify
import os, sys
from functools import wraps
import MySQLdb
from flask.ext.hashing import Hashing
import socket, threading, time
from threading import Lock

#create app object
app = Flask(__name__)

#hashing lines from hello3
#bcrypt = Bcrypt(app)
hashgun = Hashing(app)
# config
app.secret_key = os.urandom(11)


# host and port for the socket
host = '0.0.0.0'
port = 10000

#Open db connection
db = MySQLdb.connect("localhost","SGDAdmin","password","WEBAPP")

#prepare cursor object
cursor = db.cursor()

#execute SQL query
cursor.execute("SELECT VERSION()")

#Fetch table using fetchall() method
data = cursor.fetchall()

print "Database version: %s " % data
print "Database connection successful!"

# --------------------------------------------------
#Thread Stuff

mutex = Lock()
webapp_request = None
returnFlag = False
inputKey = None
check = False
load_counter = 0
results = []
tableSGDB = []

# class for threads
class New_thread (threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        print "Starting " + self.name
        runConnection(self.name)
        print "Exiting " + self.name


# This is what the thread is running in parallel with the program
def runConnection(threadName):
	print "-" * 20
	print("Running Socket Thread")
	print "-" * 20

	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                             
	serversocket.bind((host, port))                                  
	serversocket.listen(5)

	serversocket.settimeout(30)

	data = ""
	reset = False

	global returnFlag
	global webapp_request
	global inputKey
	global check
	global results 
	webapp_request = None

	while True: #accepting loop
		print "Waiting for request..."
		while True:
			if(webapp_request != None):
				print "Received a Request!!! [%s]" % webapp_request
				break
			time.sleep(0.25)

		time.sleep(2)
		reset = False
		
		try:
			print("Searching for Connection...")
			clientsocket,addr = serversocket.accept()
			print("Got a connection from %s" % str(addr))
			err = clientsocket.send(webapp_request)
			print "Request Sent"
		except:
			pass

		#if the request is empty
		if(webapp_request == None):
			print "Resetting the connection socket"
			reset = True
		

		# If web app sends a new user request
		elif (webapp_request[0] == "N"):
			data += clientsocket.recv(1024)#we only need to read once
			end = data.find("NAME_GET")
			if end != -1:
				if(err == -1):
					print("Writing Error in new user")
			else:
				print "Incoming data does not contain NAME_GET!"

		#If webapp sends a one time key request
		elif (webapp_request[0] == "O"):
			data += clientsocket.recv(1024)
			while (inputKey == None):
				time.sleep(1)

			if(data == inputKey):
				print("Keys Match!")
				check = True
			else:
				print("Invalid Key")
				check = False

		#If the webapp sends a database request
		elif(webapp_request[0] == "D"):
			time.sleep(3)

			data += clientsocket.recv(2048)#read once

			#if it is the first read, check for correct starting token
			z = data.find("SGD:") #detect starting token
			if z == -1: #if no starting token found, break connection
				print("NO STARTING KEY FOUND")
				
			results = data.split("\r\n") #split up the data and store it in list

		#If the webapp sends a remove user request
		elif(webapp_request[0] == "R"):
			data += clientsocket.recv(1024)#we only need to read once
			end = data.find("NAME_GET")
			if end != -1:
				if(err != -1):
					print("User Removed!")
				else:
					print("Writing Error in remove user")
			else:
				print "Incoming data does not contain NAME_GET!"

		elif(webapp_request[0] == "L"):
			print "Logout Request Sent to SGD"


		#Empty the request buffer and data buffer
		print "Resetting"
		print "Results table = ",
		print results
		time.sleep(1)
		webapp_request = None
		data = ""
		mutex.acquire()
		returnFlag = True
		mutex.release()

		if(not reset):
			clientsocket.close()
	serversocket.close()
# ---------------------------------------------------
	
@app.route('/register', methods=['POST','GET'])
def register():
	reguser = request.form['reguser']
	regpass = request.form['regpass']
	cursor = db.cursor()
	regpass_hash = hashgun.hash_value(regpass)
	sqlreg = "INSERT INTO user (username, password) values ('%s', '%s')" % (reguser, regpass_hash)
	cursor.execute(sqlreg)
	db.commit()
	return render_template('signup_login.html')

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/', methods=['GET', 'POST'])
def home():
	return render_template('signup_login.html')

@app.route('/Back2Welcome', methods=['GET', 'POST'])
def Back2Welcome():
	return render_template('welcome_new.html')

# -------------------Working on modifying with parallel thread--------------
#This is currenty working as intended with the socket thread
@app.route('/tagCheck',methods = ['POST','GET']) #add post and get methods to make sure
def tagCheck():
	global webapp_request
	global returnFlag

	if returnFlag:
		mutex.acquire()
		returnFlag = False
		mutex.release()
		print "Redirecting to sgdb"
		return redirect(url_for('sgdb'))

	print("Registering new tag")
	username = session.get('newName', None)

	webapp_request = "N" + username

	time.sleep(9) #Not the most efficient way, but it works for now
	
	return redirect(url_for('tagCheck'))
# ---------------------------------------------------------------------------

# -------------------Working on modifying with parallel thread--------------
#This is currenty working as intended with the socket thread
@app.route('/remove_user',methods = ['POST','GET']) #add post and get methods to make sure
def remove_user():
	global webapp_request
	global returnFlag

	if returnFlag:
		mutex.acquire()
		returnFlag = False
		mutex.release()
		print "Redirecting to sgdb"
		return redirect(url_for('sgdb'))

	print("Registering new tag")
	username = session.get('newName', None)

	webapp_request = "R" + username

	time.sleep(9) #Not the most efficient way, but it works for now
	
	return redirect(url_for('remove_user'))
# ---------------------------------------------------------------------------

# -------------------Working on modifying with parallel thread--------------
#this does the check for the one time key
# This is currently working as intended
@app.route('/nonce')
def nonceMain():

	global webapp_request
	global returnFlag
	global check
	global inputKey

	if (returnFlag and check):
		mutex.acquire()
		returnFlag = False
		check = False
		mutex.release()
		print "Redirecting to sgdb"
		return redirect(url_for('sgdb'))
	elif (returnFlag and not check):
		mutex.acquire()
		returnFlag = False
		mutex.release()
		print "Redirecting to user page"
		return redirect(url_for('home'))

	webapp_request = "O"
	inputKey = session.get('oneTimeKey', None)

	time.sleep(9)

	return redirect(url_for('nonceMain'))

# -------------------------------------------------------------------------

# -------------------Working on modifying with parallel thread--------------
#Has not yet been tested, but should be working
#reading from and displaying the database
@app.route("/sgdb", methods=['GET','POST'])
def sgdb():

	global webapp_request
	global returnFlag
	global results
	global tableSGDB
	global load_counter

	tableSGDB = []

	if returnFlag:
		load_counter = 0
		print "Loading sgdb..."
		for i in range(0,len(results)):
			tableSGDB.append(results[i])

		for i in range(len(results)-1, 11):
			tableSGDB.append(" ")

		mutex.acquire()
		returnFlag = False
		results = []
		mutex.release()

		return render_template("databasesgd.html", tableSGDB=tableSGDB)
	else:
		if load_counter < 4:
			webapp_request = "D"
			time.sleep(8)
			print("Attempting to connect to sgdb...")
			load_counter += 1
		else: #If there is a timeout
			print "--------TIMEOUT in connection--------"
			load_counter = 0
			mutex.acquire()
			webapp_request = None
			returnFlag = False
			mutex.release()
			return render_template("databasesgd_timeout.html", tableSGDB=tableSGDB)

	return redirect(url_for('sgdb'))

#adding a new user to sgdb
@app.route("/addUser", methods=['GET','POST'])
def addUser():
	name = request.form['addUser']
	session['newName'] = name
	return redirect(url_for('tagCheck'))

#removing a user from sgdb
@app.route("/removeUser", methods=['GET','POST'])
def removeUser():
	remove_name = request.form['removeUser']
	session['newName'] = remove_name
	return redirect(url_for('remove_user'))

# -------------------------------------------------------------------------

@app.route('/login', methods=['POST','GET'])
def login():
	error = None
	loguser = request.form['loguser']
	logpass = request.form['logpass']
	logpass_hash = hashgun.hash_value(logpass)
	cursor = db.cursor()
	sqllog = "SELECT * from user where username='" + loguser + "' and password='" + logpass_hash + "'"
	cursor.execute(sqllog)
	data = cursor.fetchone()
	if data is None:
		error = 'Invalid Username or Password'
		return render_template('login_signup.html')
	else:
		session['logged_in'] = True
		flash('Successfully logged in.')
		return render_template('welcome_new.html')

@app.route('/logout', methods=['POST','GET'])
@login_required
def logout():

	global webapp_request

	webapp_request = "L"
	time.sleep(1)

	session.pop('logged_in', None)
	flash('Successfully logged out.')
	return render_template('signup_login.html')

@app.route('/authorization_load', methods=['POST','GET'])
def authorization_load():
	return render_template('authorization.html')

@app.route('/authorization', methods=['POST','GET'])
def authorization():
	sgdid = request.form['sgdid']
	session['oneTimeKey'] = sgdid
	return redirect(url_for('nonceMain'))


# start the server with the 'run()' method
# In debug mode, if there is a problem, the program restarts, this creates multiple threads that 
# try to use the same port causing a socket error and preventing the program from running properly
if __name__ == '__main__':

	socket_thread = New_thread("Socket Thread")
	socket_thread.start()

	app.run()
