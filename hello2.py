# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import MySQLdb
from connect import connection
from wtforms import Form,BooleanField,TextField,PasswordField,validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thrwart
import gc
from flask.ext.bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


from flaskext.mysql import MySQL
# create the application object
app = Flask(__name__)
bcrypt = Bcrypt(app)
# config
app.secret_key = 'my precious'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'slayer'
app.config['MYSQL_DATABASE_DB'] = 'py'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route("/register")
def register():
	regname = request.form.get('username',None)
	regpw = request.form.get('password',None)
	cursor1 = mysql.connect().cursor()
	cursor1.execute("INSERT INTO user(userID,userName,password) VALUES ( (%s,%s, %s)",(1,regname,regpw))
	mysql.connect.commit()
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
@app.route('/')
@login_required
def home():
    return render_template('index.html')  # render a template
    # return "Hello, World!"  # return a string

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connect().cursor()
		cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
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
    return redirect(url_for('welcome'))

# start the server with the 'run()' method
if __name__ == '__main__':
	app.run(debug=True)