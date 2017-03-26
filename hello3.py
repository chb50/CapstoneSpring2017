# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import MySQLdb
from flask.ext.hashing import Hashing


from flaskext.mysql import MySQL
# create the application object
app = Flask(__name__)
#bcrypt = Bcrypt(app)
hashgun = Hashing(app)
# config
app.secret_key = 'my precious'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'slayer'
app.config['MYSQL_DATABASE_DB'] = 'py'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

class sgdPacket():
	def __init__(self, name, NFCtag):
		self.name = name
		self.NFCtag = NFCtag



@app.route("/register",methods=['GET','POST'])
def register():
	if request.method == 'POST':
		hello = 'hello'
		regname = request.form.get('username')
		regpw = request.form.get('password')
		conn = mysql.connect()
		cursor1 = conn.cursor()
		pwhash = hashgun.hash_value(regpw)
	#sql = "INSERT INTO user (userID,userName,password) VALUES %d,%s,%s " (10,'cedric','cedrictwin')
	#sql = "INSERT INTO user (userID, userName, password) values ('%d', '%s', '%s')" % (, regname, regpw)
		sql = "INSERT INTO user (userName, password) values ('%s', '%s')" % (regname,pwhash)
		cursor1.execute(sql)
		conn.commit()
		return redirect(url_for('login'))
	return render_template('register.html')

	#regname = request.form['username']
	#regpw = request.form['password']
	#cursor = mysql.connect().cursor()
	#cursor.execute("INSERT INTO user(userID,userName,password) VALUES ( (%d,%s, %s)",1,regname,regpw)
	#mysql.connect.commit()
	
	

@app.route("/Authenticate")
def Authenticate():
    username = request.args.get('UserName')
    password = request.args.get('Password')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
     return "Username or Password is wrong"
    else:
     return "Logged in successfully"



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

# use decorators to link the function to a url
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
	if request.method == 'POST': #code to put smartgun code into database
		regid = request.form.get('test')
		print regid
		if(regid == 'nopenopenope111'): #testing the check!  #add multiple trys
			conn1 = mysql.connect()
			cursor2 = conn1.cursor()
			sql1 = "INSERT INTO user (userName, password) values ('%s', '%s')" % (regid,regid)
			cursor2.execute(sql1)
			conn1.commit()
			return render_template('database.html')
		else:
			return render_template('index.html')  # render a template
	return render_template('index.html')  # render a template
    # return "Hello, World!"  # return a string

@app.route('/welcome',methods = ['POST','GET']) #add post and get methods to make sure
def welcome():

	table = [] 



	table.append(sgdPacket("bob","qwe123qwe123qwe"))
	table.append(sgdPacket("jillard","345ert345ert345"))
	table.append(sgdPacket("dickling","uio789uio789uio"))
	test = 1
	nameid = request.form.get("name2")
	print nameid

	for i in range(len(table)-1,10):
		table.append(sgdPacket(None, None))


	# for i in range(0,len(results)):
	# 	table.append(results[i])

	# for i in range(len(results)-1, 10):
	# 	table.append(" ")

	return render_template("database3.html", table=table, length=len(table),test = test)

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
		username = request.form['username']
		password1 = request.form['password']
		password = hashgun.hash_value(password1)
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
		#cursor.execute("SELECT * from User where Username='" + username + "'")
		data = cursor.fetchone()
		if data is None:
			return "Username or Password is wrong"
		else:
			session['logged_in'] = True
			flash('You were logged in.')
			return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))
	


# start the server with the 'run()' method
if __name__ == '__main__':
	app.run(debug=True)