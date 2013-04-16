import logging
import os
import shlex
import signal
import subprocess
import sys
import threading

import config
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
		environ = {}

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
	""" An executed command's response. """

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
			return '<Response [{0}, {1}]>'.format(self.command[0], self.status_code)
		else:
			return '<Response>'

class ExecutionCommands():
	def __init__(self, compileCmd, runCmd):
		self.compileCmd = compileCmd
		self.runCmd = runCmd

def expand_args(command):
	""" Parses command strings and returns a Popen-ready list. """

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
	""" Executes a given commmand and returns Response.
	Blocks until process is complete, or timeout is reached. """

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

def getPythonCommands(fileName):
	compileArg = None
	execArg = "python %s" % fileName
	return ExecutionCommands(compileArg, execArg)

def getJavaCommands(fileName):
	compileArg = "javac %s" % fileName

	i = fileName.rindex(".")
	progName = fileName[:i]
	execArg = "java %s" % progName

	return ExecutionCommands(compileArg, execArg)

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

def runCommands(executionCommands, stdin, expectedOutput):
	""" Tries to compile and run the given commands in subprocesses.
	Returns the appropriate status code when finished. """
	if executionCommands.compileCmd:
		compileResponse = run_command(executionCommands.compileCmd)
		result = getResult(compileResponse, expectedOutput)
		if result == status.RUNTIME_ERROR:
			return status.COMPILE_ERROR
		log.debug("Compilation successful. Attempting to run...")

	runResponse = run_command(executionCommands.runCmd, data=stdin, timeout=DEFAULT_TIMEOUT)
	return getResult(runResponse, expectedOutput)

extToMethod = {}
extToMethod[PYTHON_EXT] = getPythonCommands
extToMethod[JAVA_EXT] = getJavaCommands

def subprocessJudge(fileSource, language, stdin, expectedOutput):
	""" Runs the judge as a subprocess and passes the required
	arguments to standard in by pickling them. The judge process
	forks and runs them in a new chroot'd process. """

	cmd = "python %s" % config.JUDGE_FILE_PATH

	inputTuple = (fileSource, language, stdin, expectedOutput)
	pickledInput = subprocess.pickle.dumps(inputTuple)

	response = run_command(cmd, data=pickledInput)
	return int(response.std_out)

def executeInNewProcess(fileSource, language, stdin, expectedOutput):
	""" Forks and runs the given code in a child, chroot'd process.
	The result (AC, WA, etc.) is written to a pipe that the parent
	reads from and is returned. """
	r, w = os.pipe()
	pid = os.fork()

	if pid: # parent process
		os.close(w)
		r = os.fdopen(r) # turn r into a file object
		result = r.read()
		r.close()
		os.waitpid(pid, 0) # make sure the child process gets cleaned up
		return result
	else: # child process
		os.close(r)
		
		try:
			os.chdir(config.CHROOT_DIR)
			os.chroot('.')
			os.setuid(config.JUDGE_UID)
		except OSError as e:
			log.debug("chroot failed. Abandoning execution.")
			log.debug("%s" % e.message)
			w.write(status.INTERNAL_ERROR)
			sys.exit(1)

		result = executeProgram(fileSource, language, stdin, expectedOutput)
		result = str(result)

		w = os.fdopen(w, 'w')
		w.write(result)
		w.close()
		sys.exit(0)

def executeProgram(fileSource, language, stdin, expectedOutput):
	""" Creates a new execution directory, source file, and runs it in
	a subprocess. Cleans the directory and returns the result. """
	ext = langToExt.get(language)
	if not ext or ext not in extToMethod:
		log.debug("Invalid language: '%s'" % language)
		return None

	fileName = "template.%s" % ext

	# Create an execution directory based on the current time plus some randomness
	folderName = datetime.now().strftime("%m-%d-%Y_%H:%M:%S") + "_" + str(random())[2:10]
	runDir = 'runs/%s' % folderName

	log.debug("Creating execution directory: %s" % os.path.join(os.getcwd(), runDir))
	os.mkdir(runDir)
	log.debug("Execution directory created.")
	os.chdir(runDir)
	log.debug("chdir'd into execution directory.")

	log.debug("Creating file: %s" % fileName)
	f = file(fileName, 'w')
	f.write(fileSource)
	f.flush()
	f.close()

	log.debug("About to execute file: %s" % fileName)
	getCommandsFunc = extToMethod[ext]
	execCommands = getCommandsFunc(fileName)
	result = runCommands(execCommands, stdin, expectedOutput)

	# Move out of the execution directory and delete it.
	os.chdir("../..")
	cleanDirectory(runDir)
	return result

def cleanDirectory(runDir):
	""" Removes the given directory and all files inside of it """
	log.debug("Removing directory: %s" % os.path.join(os.getcwd(), runDir))
	for fileName in os.listdir(runDir):
		os.remove(runDir + '/' + fileName)
	os.rmdir(runDir)

if __name__=='__main__':
	# Takes a pickled tuple with the following arguments:
	# (File source, Language, Standard Input, Expected Output)
	# and runs it in a forked, chroot'd process.
	allInput = sys.stdin.read()
	unpickled = subprocess.pickle.loads(allInput)
	fileSource, language, stdin, expectedOutput = unpickled

	result = executeInNewProcess(fileSource, language, stdin, expectedOutput)
	print result
	sys.exit(0)