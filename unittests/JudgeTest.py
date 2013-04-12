from django.test import TestCase
from programmer import judge, status, languages

class DummyResult():
	def __init__(self, status_code, std_out):
		self.status_code = status_code
		self.std_out = std_out

class JudgeTest(TestCase):
	def setUp(self):
		self.HELLO_WORLD = "Hello, world!"

	def test_get_python_commands(self):
		cmds = judge.getPythonCommands("main.py")

		self.assertEqual(cmds.compileCmd, None)
		self.assertEqual(cmds.runCmd, "python main.py")

	def test_get_java_commands(self):
		cmds = judge.getJavaCommands("Main.java")

		self.assertEqual(cmds.compileCmd, "javac Main.java")
		self.assertEqual(cmds.runCmd, "java Main")

	def test_get_ac_result(self):
		dr = DummyResult(0, self.HELLO_WORLD)
		result = judge.getResult(dr, self.HELLO_WORLD)

		self.assertEqual(result, status.ANSWER_CORRECT)

	def test_get_wa_result(self):
		dr = DummyResult(0, self.HELLO_WORLD)
		result = judge.getResult(dr, self.HELLO_WORLD + "!")

		self.assertEqual(result, status.WRONG_ANSWER)

	def test_get_re_result(self):
		dr = DummyResult(-1, self.HELLO_WORLD)
		result = judge.getResult(dr, self.HELLO_WORLD)

		self.assertEqual(result, status.RUNTIME_ERROR)

	def test_get_tle_result(self):
		dr = DummyResult(-15, self.HELLO_WORLD)
		result = judge.getResult(dr, self.HELLO_WORLD)

		self.assertEqual(result, status.TIME_LIMIT_EXCEEDED)

	def test_execute_program(self):
		source = "print '%s'" % self.HELLO_WORLD
		language = languages.PYTHON
		stdin = ""
		expectedOutput = self.HELLO_WORLD
		result = judge.executeProgram(source, language, stdin, expectedOutput)

		self.assertEqual(result, status.ANSWER_CORRECT)

	def test_execute_in_new_process(self):
		source = "print '%s'" % self.HELLO_WORLD
		language = languages.PYTHON
		stdin = ""
		expectedOutput = self.HELLO_WORLD
		result = judge.executeProgram(source, language, stdin, expectedOutput)

		self.assertEqual(result, status.ANSWER_CORRECT)

	def test_subprocess_judge(self):
		source = "print '%s'" % self.HELLO_WORLD
		language = languages.PYTHON
		stdin = ""
		expectedOutput = self.HELLO_WORLD
		result = judge.subprocessJudge(source, language, stdin, expectedOutput)

		self.assertEqual(result, status.ANSWER_CORRECT)