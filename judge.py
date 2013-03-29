import logging
import os
import shlex
import signal
import subprocess
import sys
import threading

import status

from datetime import datetime
from random import random
from languages import PYTHON, JAVA, PYTHON_EXT, JAVA_EXT

DEFAULT_TIMEOUT = 5

langToExt = {}
langToExt[JAVA] = JAVA_EXT
langToExt[PYTHON] = PYTHON_EXT

log = logging.getLogger(__name__)

def terminate_process(process):
	os.kill(process.pid, signal.SIGTERM)

def kill_process(process):
	os.kill(process.pid, signal.SIGKILL)

def thread_is_alive(thread):
	if hasattr(thread, "is_alive"):
		return thread.is_alive()
	else:
		return thread.isAlive()

class Command(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = None
		self.out = None
		self.err = None
		self.returncode = None
		self.data = None
		self.exc = None

	def run(self, data, timeout, kill_timeout, env, cwd):
		self.data = data
		environ = dict(os.environ)
		environ.update(env or {})

		def target():
			try:
				self.process = subprocess.Popen(self.cmd,
					universal_newlines=True,
					shell=False,
					env=environ,
					stdin=subprocess.PIPE,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					bufsize=0,
					cwd=cwd,
				)

				if sys.version_info[0] >= 3: # Python 3 support
					self.out, self.err = self.process.communicate(
						input = bytes(self.data, "UTF-8") if self.data else None 
					)
				else:
					self.out, self.err = self.process.communicate(self.data)
			except Exception as exc:
				self.exc = exc
		
		thread = threading.Thread(target=target)

		thread.start()
		thread.join(timeout)

		if self.exc:
			raise self.exc

		if thread_is_alive(thread):
			terminate_process(self.process)
			thread.join(kill_timeout)
			if thread_is_alive(thread):
				kill_process(self.process)
				thread.join()

		self.returncode = self.process.returncode

		return self.out, self.err

class Response(object):
	"""An executed command's response"""

	def __init__(self, process=None):
		super(Response, self).__init__()

		self.process = process
		self.command = None
		self.std_err = None
		self.std_out = None
		self.status_code = None
		self.history = []


	def __repr__(self):
		if len(self.command):
			return '<Response [{0}]>'.format(self.command[0])
		else:
			return '<Response>'

def expand_args(command):
    """Parses command strings and returns a Popen-ready list."""

    # Prepare arguments.
    if isinstance(command, str):
        splitter = shlex.shlex(command)
        splitter.whitespace = '|'
        splitter.whitespace_split = True
        command = []

        while True:
            token = splitter.get_token()
            if token:
                command.append(token)
            else:
                break

        command = list(map(shlex.split, command))

    return command

def run_command(command, data=None, timeout=None, kill_timeout=None, env=None, cwd=None):
    """Executes a given commmand and returns Response.

    Blocks until process is complete, or timeout is reached.
    """

    command = expand_args(command)
    history = []
    for c in command:

        if len(history):
            # due to broken pipe problems pass only first 10 KiB
            data = history[-1].std_out[0:10*1024]

        cmd = Command(c)
        out, err = cmd.run(data, timeout, kill_timeout, env, cwd)

        r = Response(process=cmd)

        r.command = c
        r.std_out = out
        r.std_err = err
        r.status_code = cmd.returncode

        history.append(r)

    r = history.pop()
    r.history = history

    return r

def runPython(fileName, stdin, expectedOutput):
	""" Runs the given Python file with the given input. Returns
	the proper status code based on the run succeeding and the
	expected output being matched. """

	execArg =  "python %s" % fileName
	r = run_command(execArg, data=stdin, timeout=DEFAULT_TIMEOUT)
	return getResult(r, expectedOutput)
	
def runJava(fileName, stdin, expectedOutput):
	""" Compiles and runs the given Java file with the given input.
	Returns the proper status code based on compilation succeeding
	and the expected output being matched. """

	compileArg = "javac %s" % fileName
	r = run_command(compileArg, timeout=DEFAULT_TIMEOUT)
	
	if r.statusCode != 0:
		return status.COMPILE_ERROR

	i = fileName.rindex(".")
	progName = fileName[:i]
	execArg = "java %s" % progName

	r = run_command(execArg, data=stdin, timeout=DEFAULT_TIMEOUT)
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

def executeProgram(fileSource, language, stdin, expectedOutput):
	ext = langToExt.get(language)
	if not ext:
		log.debug("Invalid language: '%s'" % language)
		return None

	name = "template.%s" % ext

	folderName = datetime.now().strftime("%m-%d-%Y_%H:%M:%S") + "_" + str(random())[2:10]
	
	currDir = os.path.dirname(os.path.realpath(__file__))
	runDir = currDir + "/runs/%s" % folderName
	
	log.debug("Creating execution directory: %s" % runDir)
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