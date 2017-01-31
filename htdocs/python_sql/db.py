#mysql db using python

import mysql.connector
from mysql.connector import errorcode

conn = mysql.connector.connect(user='root', password='password', host='localhost',database='authorization')
conn.close()

try:

	conn = mysql.connector.connect(
			user = 'root',
			password = 'password',
			host = 'localhost'
			database = 'authorization'
			)
			
except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
	print("wrong username or password")
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
	print("database not found")
	else:
	print(err)
else:
conn.close()

DB_NAME = 'authorization'
TABLES = {}

TABLES['login'] = (
	"CREATE TABLE 'login' ("
	"	'username' varchar(12) NOT NULL,"
	"	'password' varchar(12) NOT NULL"
	")	ENGINE=InnoDB")

conn = mysql.connector.connect(user='root')
cursor = conn.cursor()

def create_database(cursor):
	try:
		cursor.execute(
			"CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
	except mysql.connector.Error as err:
		print("database failed to create: {}".format(err))
		exit(1)
		
try:
	conn.database = DB_NAME
except mysql.connector.Error as err:
	if err.errno == erorcode.ER_BAD_DB_ERROR:
	create_database(cursor)
	conn.database = DB_NAME
	else:
		print(err)
		exit(1)

for name, ddl in TABLES.iteritems():
	try:
		print("creating table {}: ".format(name), end='')
		cursor.execute(ddl)
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
			print("already exists.")
		else:
			print(err.msg)
	else:
		print("OK")
		
add_login = ("INSERT INTO login "
				"(username, password)"
				"VALUES (%s, %s)")
				
data_login = ('testuser', 'testpass')
cursor.execute(add_login, data_login)

conn.commit()

cursor.close()
conn.close()

			