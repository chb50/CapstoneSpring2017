from flask import Flask, render_template, request, redirect, url_for
from flask import session, flash
from flask import jsonify
import os
from functools import wraps
import MySQLdb
from flask.ext.hashing import Hashing
import socket

#create app object
app = Flask(__name__)

#hashing lines from hello3
#bcrypt = Bcrypt(app)
hashgun = Hashing(app)
# config
app.secret_key = os.urandom(11)



port = 10001

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
		#Open db connection

	db = MySQLdb.connect("localhost","root","password","py")

	#prepare cursor object
	cursor = db.cursor()

	#execute SQL query
	cursor.execute("SELECT VERSION()")

	#Fetch table using fetchall() method
	data = cursor.fetchall()

	print "Database version: %s " % data
	print "Database connection successful!"
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
# @login_required
def home():
	return render_template('homepage.html')
	
@app.route('/welcome',methods = ['POST','GET']) #add post and get methods to make sure
def welcome():

	serversocket = openSocket()
	newRequest, clientsocket = readRequest(serversocket)

	print clientsocket

	test = 1
	nameid = request.form.get("name2")

	#test value for now
	nameid = "TESTVALUE\0"

	if newRequest: #if it is a new request
		print("Write Back Function")
		print("Writing to Socket...")
		print(clientsocket)
		err = clientsocket.send(nameid)
		if(err != -1):
			print("Write Successful")
			clientsocket.close()
		else:
			print("Writing Error")
			clientsocket.close()
	serversocket.close()
	
	return render_template("database3.html",test = newRequest)

def openSocket():
	print("Open Socket Function")
		# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

	# universal name
	host = '0.0.0.0';                                                    

	# bind to the port
	serversocket.bind((host, port))                                  

	# queue up to 5 requests
	serversocket.listen(5)

	return serversocket

def readRequest(serversocket):
	print("Read request function")
	data = ""

	print("Searching for new tags...")
	clientsocket,addr = serversocket.accept()
	print("Got a connection from %s" % str(addr))

	data += clientsocket.recv(1024)#we only need to read once

	end = data.find("NEW")
	if end != -1:
		return True, clientsocket
	else:
		clientsocket.close()
		serversocket.close()
		return False, 0
	
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
		return "Username or Password is invalid."
	else:
		session['logged_in'] = True
		flash('Successfully logged in.')
		return render_template('homepage.html')

@app.route('/logout', methods=['POST','GET'])
@login_required
def logout():
	session.pop('logged_in', None)
	flash('Successfully logged out.')
	return render_template('login.html')


@app.route('/nonce')
def nonceMain():

	inputKey = session.get('oneTimeKey', None)

	# inkey = "SGD:OFPKLXMPWRG"
	# check = compareKey(inputKey)

	check = False

	print check

	if check:
		return redirect(url_for('welcome'))
	else:
		return redirect(url_for('home'))

	return render_template('randomTemplate.html')


def compareKey(key):
	print("Open Socket for One Time Key")
	print("Input value = " + key)
	request = "O" #this is the request for the one time key
		# create a socket object
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

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
@app.route("/sgddatabase")
def main():

	results = connection()

	table = [] 

	for i in range(0,len(results)):
		table.append(results[i])

	for i in range(len(results)-1, 11):
		table.append(" ")
	print table

	return render_template("databasesgd.html", table=table, length=len(results))

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
				clientsocket.close();
				return table

			r = data.find("\r\n")#detect ending line token
			if r != -1:# if ending line token is detected
				i = i+1 # increment index
				table.append(data) # add the data to the table
				data = "" # empty the data buffer
	clientsocket.close();


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
if __name__ == '__main__':
	app.run(debug=True)