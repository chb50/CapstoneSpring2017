from flask import Flask, render_template, request, redirect, url_for
from flask import session, flash
from flask import jsonify
import os
from functools import wraps
import MySQLdb
from flask.ext.hashing import Hashing
import socket, threading, time

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

webapp_request = None
returnFlag = False
inputKey = None
check = False
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

	data = ""

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
			
		print("Searching for Connection...")
		clientsocket,addr = serversocket.accept()
		print("Got a connection from %s" % str(addr))

		err = clientsocket.send(webapp_request)
		print "Request Sent"

		# If web app sends a new user request
		if (webapp_request[0] == "N"):
			data += clientsocket.recv(1024)#we only need to read once
			end = data.find("NEW")
			if end != -1:
				if(err != -1):
					print("New User Added!")
					clientsocket.close()
				else:
					print("Writing Error in new user")
					clientsocket.close()
			else:
				print "Incoming data does not contain NEW!"

		#If webapp sends a one time key request
		elif (webapp_request[0] == "O"):
			print("Waiting to Receive data...")
			data += clientsocket.recv(1024)
			print("Data Received, Comparing...")
			while (inputKey == None):
				time.sleep(1)

			print "Comparing keys"
			if(data == inputKey):
				print("Keys Match!")
				check = True
			else:
				print("Invalid input")
				check = False

		#If the webapp sends a database request
		elif(webapp_request[0] == "D"):
			i = 0
			while True: #reading loop
				data += clientsocket.recv(1024)#read once

				if i == 0: #if it is the first read, check for correct starting token
					z = data.find("SGD:") #detect starting token
					if z == -1: #if no starting token found, break connection
						print("NO STARTING KEY FOUND")
						break

				end = data.find("SGD:END") #if the final end token is detected, break
				if end != -1:
					#This is where we end
					break

				r = data.find("\r\n")#detect ending line token
				if r != -1:# if ending line token is detected
					i = i+1 # increment index
					results.append(data) # add the data to the table
					data = "" # empty the data buffer

		#Empty the request buffer and data buffer
		time.sleep(1)
		webapp_request = None
		data = ""
		returnFlag = True

		clientsocket.close()
	serversocket.close()
# ---------------------------------------------------

#sgd packet class from hello3
class sgdPacket():
	def __init__(self, name, NFCtag):
		self.name = name
		self.NFCtag = NFCtag

@app.route('/register_load', methods=['POST','GET'])
def register_load():
	return render_template('register.html')
	
@app.route('/register', methods=['POST','GET'])
def register():
	reguser = request.form['reguser']
	regpass = request.form['regpass']
	cursor = db.cursor()
	regpass_hash = hashgun.hash_value(regpass)
	sqlreg = "INSERT INTO user (username, password) values ('%s', '%s')" % (reguser, regpass_hash)
	cursor.execute(sqlreg)
	db.commit()
	return render_template('homepage.html')

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
	return render_template('homepage.html')

@app.route('/Back2Welcome', methods=['GET', 'POST'])
def Back2Welcome():
	return render_template('welcome_new.html')

#stuff for new tag input
@app.route('/tagInput', methods=['POST','GET'])
def tagInput():
	return render_template('addTag.html')

@app.route('/newTagRequest', methods=['POST','GET'])
def newTagRequest():
	name = request.form['name']
	session['newName'] = name
	return redirect(url_for('tagCheck'))


# -------------------Working on modifying with parallel thread--------------
#This is currenty working as intended with the socket thread
@app.route('/tagCheck',methods = ['POST','GET']) #add post and get methods to make sure
def tagCheck():
	global webapp_request
	global returnFlag

	if returnFlag:
		returnFlag = False
		print "Redirecting to sgdb"
		return redirect(url_for('sgdb'))

	print("Registering new tag")
	username = session.get('newName', None)

	webapp_request = "N" + username

	time.sleep(10) #Not the most efficient way, but it works for now
	
	return redirect(url_for('tagCheck'))
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
		returnFlag = False
		check = False
		print "Redirecting to sgdb"
		return redirect(url_for('sgdb'))
	elif (returnFlag and not check):
		returnFlag = False
		print "Redirecting to user page"
		return redirect(url_for('home'))

	webapp_request = "O"
	inputKey = session.get('oneTimeKey', None)

	time.sleep(10)

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

	if returnFlag:
		return render_template("databasesgd.html", table=tableSGDB, length=len(results))
	else:
		time.sleep(5)

	webapp_request = "D"
	print("Connecting to sgdb...")
	time.sleep(10)

	for i in range(0,len(results)):
		tableSGDB.append(results[i])

	for i in range(len(results)-1, 11):
		tableSGDB.append(" ")
	print tableSGDB

	return redirect(url_for('sgdb'))
# -------------------------------------------------------------------------

# route for handling the login page logic
@app.route('/login_load', methods=['POST','GET'])
def login_load():
	return render_template('login.html')

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
		return render_template('login.html')
	else:
		session['logged_in'] = True
		flash('Successfully logged in.')
		return render_template('welcome_new.html')

@app.route('/logout', methods=['POST','GET'])
@login_required
def logout():
	session.pop('logged_in', None)
	flash('Successfully logged out.')
	return render_template('login.html')

<<<<<<< HEAD

#this does the check for the one time key
@app.route('/nonce')
def nonceMain():

	print("Checking one time key")

	inputKey = session.get('oneTimeKey', None)

	# inkey = "SGD:OFPKLXMPWRG"
	check = compareKey(inputKey)

	print check

	if check:
		return redirect(url_for('sgdb'))
	else:
		return redirect(url_for('home'))


def compareKey(key):
	print("Open Socket for One Time Key")
	print("Input value = " + key)
	request = "O" #this is the request for the one time key
		# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

	# universal name
	host = '0.0.0.0';                                                    

	# bind to the port
	serversocket.bind((host, port))                                  

	# queue up to 5 requests
	serversocket.listen(5)

	data = ""

	print("Searching for connection...")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))

	print("Request Sent")
	clientsocket.send(request)

	print("Waiting to Receive data...")
	data += clientsocket.recv(1024)

	print("Data Received, Comparing...")
	if(data == key):
		print("Keys Match!")
		clientsocket.close()
		serversocket.close()
		return True
	else:
		print("Invalid input")
		clientsocket.close()
		serversocket.close()
		return False


#reading from and displaying the database
@app.route("/sgdb", methods=['GET','POST'])
def sgdb():

	print("Connecting to sgdb")

	results = connection()

	table = [] 

	for i in range(0,len(results)):
		table.append(results[i])

	for i in range(len(results)-1, 11):
		table.append(" ")
	print table

	return render_template("databasesgd.html", table=table, length=len(results))

#adding a new user to sgdb
@app.route("/addUser", methods=['GET','POST'])
def addUser():
	addUser=request.form['addUser']

#removing a user from sgdb
@app.route("/removeUser", methods=['GET','POST'])
def removeUser():
	removeUser=request.form['removeUser']

def connection():
	print("Running connection")
		# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

	# universal name
	host = '0.0.0.0';                                                            

	# bind to the port
	serversocket.bind((host, port))                                  

	# queue up to 5 requests
	serversocket.listen(5)                                           

	data = ""
	i = 0
	table = []

	request = "D" #This tell the arduino that we want the database

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
				serversocket.close()
				clientsocket.close()
				return table

			r = data.find("\r\n")#detect ending line token
			if r != -1:# if ending line token is detected
				i = i+1 # increment index
				table.append(data) # add the data to the table
				data = "" # empty the data buffer
	clientsocket.close()


=======
>>>>>>> 9f69621f8d0df908491faa99a2ae61c48caf87df
@app.route('/authorization_load', methods=['POST','GET'])
def authorization_load():
	return render_template('authorization.html')

@app.route('/authorization', methods=['POST','GET'])
def authorization():
	sgdid = request.form['sgdid']
	session['oneTimeKey'] = sgdid
	return redirect(url_for('nonceMain'))

@app.route('/DeviceAuthorization_load', methods=['POST','GET'])
def DeviceAuthorization_load():
	return render_template('DeviceAuthorization.html')

#Route to submit form data in database and display it in browser

@app.route('/DeviceAuthorization', methods=['POST','GET'])
def DeviceAuthorization():
	user = request.form['UserName']
	sgd = request.form['sgd_ID']
	cursor = db.cursor()
	radio_btn_val = request.form['authorization']
	if radio_btn_val == 'authorize':
		sqli = "INSERT INTO sgdauth (UserName, sgd_ID) values ('%s', '%s')" % (user, sgd)
		cursor.execute(sqli)
	if radio_btn_val == 'unauthorize':
		sqli = "DELETE FROM sgdauth WHERE UserName=%s AND sgd_ID=%s"
		cursor.execute(sqli, (user,sgd,))
	db.commit()
	cursor=db.cursor()
	sqls = "SELECT * FROM sgdauth"
	cursor.execute(sqls)
	db_data = cursor.fetchall()
	tbl = "<table style='border:1px solid blue'>"
	for row in db_data:
		tbl = tbl + "<tr>"
		for data in row:
			tbl = tbl + "<td>" + str(data) + "</td>"
		tbl = tbl + "</tr>"
	return "<html><body>" + tbl + "</body></html>"



# start the server with the 'run()' method
# debug causes multiple threads to run, giving an error in the socket connection
if __name__ == '__main__':

	socket_thread = New_thread("Socket Thread")
	socket_thread.start()

	app.run()