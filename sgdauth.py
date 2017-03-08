from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
import MySQLdb
app = Flask(__name__)

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

#Route to HTML form in python

@app.route('/')
def form():
	return render_template('DeviceAuthorization.html')

#Route to submit form data in database and display it in browser

@app.route('/submission', methods=['POST'])
def submission():
	user = request.form['UserName']
	sgd = request.form['sgd_ID']
	cursor = db.cursor()
	sqli = "INSERT INTO sgdauth (UserName, sgd_ID) values ('%s', '%s')" % (user, sgd)
	cursor.execute(sqli)
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
	
if __name__ == "__main__":
	app.run()