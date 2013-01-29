import logging
import time
from SOAPpy import WSDL
from secret import IDEONE_USER, IDEONE_PASSWORD

# creating wsdl client
wsdl = WSDL.Proxy('http://ideone.com/api/1/service.wsdl')
user = IDEONE_USER
password = IDEONE_PASSWORD

NO_ERROR = 'OK'

# STATUS_STILL_IN_QUEUE < 0
STATUS_DONE = 0
STATUS_COMPILING = 1
STATUS_RUNNING = 2

RESULT_NOT_RUNNING = 0 # run parameter set to False
RESULT_COMPILE_ERROR = 11
RESULT_RUNTIME_ERROR = 12
RESULT_TIME_LIMIT_EXCEEDED = 13
RESULT_SUCCESS = 15
RESULT_MEMORY_LIMITED_EXCEEDED = 17
RESULT_ILLEGAL_SYSTEM_CALL = 19
RESULT_INTERNAL_ERROR = 20 # Error on IDEone's side of things

errorStrings = {}
errorStrings[RESULT_NOT_RUNNING] = "Not Running"
errorStrings[RESULT_COMPILE_ERROR] = "Compile Error"
errorStrings[RESULT_RUNTIME_ERROR] = "Runtime Error"
errorStrings[RESULT_TIME_LIMIT_EXCEEDED] = "Time Limit Exceeded"
errorStrings[RESULT_SUCCESS] = "Ran Successfully"
errorStrings[RESULT_MEMORY_LIMITED_EXCEEDED] = "Memory Limit Exceeded"
errorStrings[RESULT_ILLEGAL_SYSTEM_CALL] = "Illegal System Call"
errorStrings[RESULT_INTERNAL_ERROR] = "Internal Error"

JAVA_ID = 55
PYTHON_ID = 4

JAVA_STRING = 'Java'
PYTHON_STRING = 'Python'

languageIds = {}
languageIds[JAVA_STRING] = JAVA_ID
languageIds[PYTHON_STRING] = PYTHON_ID

def createSubmission(sourceCode, languageID, input, run=True):
	""" Creates a submission on IDEone and returns the link ID,
	or None if there's an error. """
	try:
		result = wsdl.createSubmission(user, password, sourceCode, languageID, input, run)
		d = getResultDict(result)
		return d['link']
	except:
		print "Error creating submission"
		return None

def isSubmissionFinished(link):
	""" Returns a negative number if submission is not running yet, a positive
	result code if it is done, and None if there's an error. """
	try:
		res = wsdl.getSubmissionStatus(user, password, link)
		d = getResultDict(res)
		if d['error'] != NO_ERROR:
			return None

		status = d['status']
		result = d['result']

		if status == STATUS_DONE:
			return result
		else:
			return -1
	except:
		return None

def getSubmissionOutput(link):
	""" Returns the submission output of a finished submission for the given
	link. """
	try:
		res = wsdl.getSubmissionDetails(user, password, link, False, False,
										True, False, False)
		d = getResultDict(res)

		if d['error'] != NO_ERROR:
			return None

		output = d['output']
		return output

	except:
		return None

def submitAndReturnOutput(sourceCode, language, input):
	""" Creates a runnable submission and checks on its status until it is
	done running. Returns the output as a string if it succeeded. Returns a
	positive integer if there was a compile error, runtime error, etc. Returns
	None if there was an internal error on ideone. """
	languageID = languageIds[language]
	link = createSubmission(sourceCode, languageID, input)
	if not link:
		return None

	done = False
	attempts = 0

	while not done:
		time.sleep(2)	# delay execution for 2 seconds
		done = isSubmissionFinished(link)
		if done == None:
			return None
		if done > 0:
			break
		if attempts >= 10:
			return None
		else:
			attempts = attempts+1

	if done == RESULT_SUCCESS:
		output = getSubmissionOutput(link)
		return output
	else:
		return done

def getResultDict(result):
	d = {}
	for pair in result.item:
		d[pair.key] = pair.value
	return d

def getLanguages():
	d = {}
	result = wsdl.getLanguages(user, password)
	for pair in result['item'][1][1][0]:
		d[pair['key']] = pair['value']
		d[pair['value']] = pair['key']
	return d

link = 'xBcit3'
if __name__ == '__main__':
	# print getSubmissionOutput(user, password, link)
	# print getLanguages()
	print 1
	logging.basicConfig(level=logging.DEBUG)
	print 2
	logging.info("Info!")
	print 3
	print submitAndReturnOutput('print "500\\n"', 4, "")
	