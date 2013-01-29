import cgi
import logging
import multiprocessing
import MySQLdb
import os
import web

import IdeoneHelper
from handler import Handler
from problem import Problem

web.config.debug = True

db = MySQLdb.connect("localhost", "root", "password", "MyDatabase")

urls = (
	'/main/?', 'Main',
	'/problems/([A-Z]+)', 'ProblemPage',
	'/problems/judge/([A-Z]+)', 'Judge',
	'/problems/?', 'AllProblemsPage',
	)

def escape_html(s):
	return cgi.escape(s, quote=True)

class Main(Handler):
	def GET(self):
		return self.render('main.html')

class AllProblemsPage(Handler):
	def GET(self):
		problems = Problem.getAllProblems()
		count = len(problems)
		return self.render('problems.html', problems=problems, count=count)

templates = ['java', 'py']
class ProblemPage(Handler):
	def GET(self, name):
		problem = Problem.getProblemByName(name)
		if not problem:
			return "Problem %s doesn't exist." % name
		
		problemPath = 'problems/%s/' % name

		sourceDict = {}
		for ext in templates:
			fileName = os.path.join(os.path.dirname(__file__), problemPath, 'templates/template.%s')
			fileName = fileName % ext
			f = open(fileName, 'r')
			
			sourceCode = f.read()
			sourceDict[ext] = sourceCode

		foldsDict = {}
		f = open(os.path.join(problemPath + 'folds.info'), 'r')
		foldsInfo = f.read()
		f.close()
		for line in foldsInfo.split("\n"):
			parts = line.split(" ")
			lang = parts[0]
			foldsDict[lang] = [int(parts[i]) for i in range(1,len(parts))]
		
		logging.debug("Folds dict: %s" % foldsDict)
		logging.debug("Rendering Problem %s" % problem.name)
		return self.render("problem.html", problem=problem, sourceDict=sourceDict,
											foldsDict=foldsDict)

	def POST(self, name):
		language = self.getParam('language')
		sourceCode = self.getParam('editor')
		logging.debug("Language: %s" % language)
		return "Problem: %s \n\nLanguage: %s \n\nSource: %s" % (name, language, sourceCode)

class Judge(Handler):
	def POST(self, name):
		language = self.getParam('language')
		sourceCode = self.getParam('editor')

		inputFileName = os.path.join(os.path.dirname(__file__), 'problems/%s/input')
		inputFileName = inputFileName % name
		inputString = open(inputFileName, 'r').read()

		outputFileName = os.path.join(os.path.dirname(__file__), 'problems/%s/output')
		outputFileName = outputFileName % name
		outputString = open(outputFileName, 'r').read()

		result = IdeoneHelper.submitAndReturnOutput(sourceCode, language, inputString)
		logging.debug(" Output string:\n%s" % outputString)
		try:
			if result <= 20:
				logging.debug("Result is less than 20.")
				return IdeoneHelper.errorStrings[result]
			else:
				int('abc')
		except:
			logging.debug("Comparing strings...")
			logging.debug(" Result string:\n%s" % result)
			if result.strip() == outputString.strip():
				logging.debug("AC!")
				return "Answer Correct"
			else:
				logging.debug("WA!")
				return "Wrong Answer"

if __name__ == "__main__": 
	logging.basicConfig(level=logging.DEBUG, filename="log.txt") # filename='example.log'
	app = web.application(urls, globals())
	# multiprocessing.Process(target=app.run).start()
    # webbrowser.open_new_tab("http://0.0.0.0:8080/")
	app.run()