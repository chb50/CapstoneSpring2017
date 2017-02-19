from flask import Flask, render_template
import os, sys, socket
from flask_mysqldb import MySQL

#In the database make the date and time a char of length 10

#authenticate the user with mysql 
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_HOST'] = '172.27.163.117'
app.config['MYSQL_USER'] = 'stone'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'testmcu'
mysql.init_app(app)

HOST = 'localhost'
PORT = 15000

@app.route("/testconnection")
def connection():
	sid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sid.bind((HOST, PORT))
	sid.listen(1)
	conn, addr = sid.accept()

	print 'Connected by' , addr

	while 1:
		data = conn.recv(1024) #create a buffer of size
		if not data: break #
		conn.sendall(data)
	conn.close()
	return data;

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

