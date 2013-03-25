#!/usr/bin/python
import argparse
import envoy
import logging
import os
import status
import time
import uuid

from languages import PYTHON, JAVA, PYTHON_EXT, JAVA_EXT

DEFAULT_TIMEOUT = 5


langToExt = {}
langToExt[JAVA] = JAVA_EXT
langToExt[PYTHON] = PYTHON_EXT

log = logging.getLogger(__name__)

def runPython(fileName, stdin, expectedOutput):
	""" Runs the given Python file with the given input. Returns
	the proper status code based on the run succeeding and the
	expected output being matched. """

	execArg =  "python %s" % fileName
	r = envoy.run(execArg, data=stdin, timeout=DEFAULT_TIMEOUT)
	return getResult(r, expectedOutput)
	
def runJava(fileName, stdin, expectedOutput):
	""" Compiles and runs the given Java file with the given input.
	Returns the proper status code based on compilation succeeding
	and the expected output being matched. """

	compileArg = "javac %s" % fileName
	r = envoy.run(compileArg, timeout=DEFAULT_TIMEOUT)
	
	if r.statusCode != 0:
		return status.COMPILE_ERROR

	i = fileName.rindex(".")
	progName = fileName[:i]
	execArg = "java %s" % progName

	r = envoy.run(execArg, data=stdin, timeout=DEFAULT_TIMEOUT)
	return getResult(r, expectedOutput)

extToMethod = {}
extToMethod[PYTHON_EXT] = runPython
extToMethod[JAVA_EXT] = runJava

def getResult(response, expectedOutput):
	""" Returns AC, WA, TLE, or RE depending on process status and output.
	AC: Process status was 0, output matches
	WA: Process status was 0, output doesn't match
	TLE: Process status was -15 (what envoy uses for TLE)
	RE: Process status was not 0, there was an error. """

	if response.status_code == -15:
		return status.TIME_LIMIT_EXCEEDED
	elif response.status_code != 0:
		return status.RUNTIME_ERROR
	else:
		if response.std_out.strip() == expectedOutput.strip():
			return status.ANSWER_CORRECT
		else:
			return status.WRONG_ANSWER
	return status.INTERNAL_ERROR

def executeProgram(fileSource, language, stdin, expectedOutput):
	log.debug("About to execute a %s program" % language)
	ext = langToExt.get(language)
	if not ext:
		log.debug("Invalid language: '%s'" % language)
		return None

	log.debug("Creating execution directory...")
	name = "template.%s" % ext
	runDir = "/home/guth/Desktop/mysite/programmer/runs/%s" % time.time()
	os.mkdir(runDir)
	fileName = "%s/%s" % (runDir, name)

	log.debug("Creating file: %s" % fileName)
	f = file(fileName, 'w')
	f.write(fileSource)
	f.flush()
	f.close()

	log.debug("About to execute file: %s" % fileName)
	runFunc = extToMethod[ext]
	result = runFunc(fileName, stdin, expectedOutput)
	cleanDirectory(runDir)
	return result

def cleanDirectory(runDir):
	""" Removes the given directory and all files inside of it """
	log.debug("Removing directory: %s" % runDir)
	for fileName in os.listdir(runDir):
		os.remove(runDir + '/' + fileName)
	os.rmdir(runDir)