import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost","root","password","MyDatabase")

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()

print "Database version: %s " % data

cursor.execute("SELECT * FROM Problems")
data = cursor.fetchall()

print "There are %d Problems:" % cursor.rowcount
for row in data:
	print row

# disconnect from server
db.close()