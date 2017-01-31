from flask import Flask, render_template
import os, sys
from flask_mysqldb import MySQL

#route root html page to authorization.html (will change to front page later)
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'capstone'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'TESTMCU'
mysql.init_app(app)

@app.route("/")
def main():
	#connect to database
	cur = mysql.connect.cursor()
	cur.execute('''SELECT * FROM TESTTABLE''')
	rv = cur.fetchall()
	return str(rv)#render_template("authorization.html")

if __name__ == "__main__":

	app.run(debug = True)

