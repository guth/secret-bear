import MySQLdb

class Problem:
	def __init__(self, name, problemStatement, description):
		self.name = name
		self.problemStatement = problemStatement
		self.description = description

	def __repr__(self):
		return "<Problem: %s, %s, %s>" % (self.name, self.problemStatement, self.description)

	@staticmethod
	def getProblemByName(name):
		query = "SELECT Name, ProblemStatement, Description FROM Problems WHERE Name='%s'" % name
		db = MySQLdb.connect("localhost","root","password","MyDatabase")
		cursor = db.cursor()
		cursor.execute(query)
		data = cursor.fetchone()
		db.close()
		
		if not data:
			return None
		return Problem(data[0], data[1], data[2])
	
	@staticmethod
	def getAllProblems():
		query = "SELECT Name, ProblemStatement, Description FROM Problems"
		db = MySQLdb.connect("localhost", "root", "password", "MyDatabase")
		cursor = db.cursor()
		cursor.execute(query)
		data = cursor.fetchall()
		db.close()

		problems = []
		for row in data:
			p = Problem(row[0], row[1], row[2])
			problems.append(p)
		return problems


