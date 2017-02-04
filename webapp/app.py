from flask import Flask, render_template
import os, sys
from flask_mysqldb import MySQL

#authenticate the user with mysql 
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

	#execute the sql command
	sql = "SELECT * FROM TESTTABLE"
	cur.execute(sql)

	results = cur.fetchall()
	table = [] 

	for i in range(0,len(results)):
		table.append(results[i])

	for i in range(len(results)-1, 10):
		table.append(" ")

	return render_template("database.html", table=table, length=len(results))

if __name__ == "__main__":
	app.run(debug = True)

