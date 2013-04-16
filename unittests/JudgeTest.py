from django.test import TestCase
from programmer import judge, status, languages

class DummyResult():
	def __init__(self, status_code, std_out):
		self.status_code = status_code
		self.std_out = std_out

class JudgeTest(TestCase):
	def setUp(self):
		self.HELLO_WORLD = "Hello, world!"
		self.PYTHON_SOURCE = "print '%s'" % self.HELLO_WORLD
		self.JAVA_SOURCE = """
class template
{
	public static void main(String[] args) throws Exception
	{
		template t = new template();
		t.go();
	}

	public void go() throws Exception
	{
		System.out.println("%s");
	}
}""" % self.HELLO_WORLD
		self.JAVA_SOURCE_RUNTIME_ERROR = """
class template
{
	public static void main(String[] args) throws Exception
	{
		template t = new template();
		t.go();
	}

	public void go() throws Exception
	{
		int[] a = new int[5];
		for(int i=0; i<=a.length; i++)
			a[i] = i;
		System.out.println("Foo");
	}
}"""

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

	def test_execute_program_python(self):
		source = self.PYTHON_SOURCE
		language = languages.PYTHON
		stdin = ""
		expectedOutputs = [self.HELLO_WORLD, "!!"]
		expectedResults = [status.ANSWER_CORRECT, status.WRONG_ANSWER]

		for i in range(len(expectedOutputs)):
			result = judge.executeProgram(source, language, stdin, expectedOutputs[i])
			self.assertEqual(result, expectedResults[i])

		wrongSource = "foo"
		result = judge.executeProgram(wrongSource, language, stdin, "")
		self.assertEqual(result, status.RUNTIME_ERROR)

		infiniteSource = "while True: pass"
		result = judge.executeProgram(infiniteSource, language, stdin, "")
		self.assertEqual(result, status.TIME_LIMIT_EXCEEDED)

	def test_execute_program_java(self):
		source = self.JAVA_SOURCE
		language = languages.JAVA
		stdin = ""
		expectedOutputs = [self.HELLO_WORLD, "!!"]
		expectedResults = [status.ANSWER_CORRECT, status.WRONG_ANSWER]
		
		for i in range(len(expectedOutputs)):
			result = judge.executeProgram(source, language, stdin, expectedOutputs[i])
			self.assertEqual(result, expectedResults[i])

		wrongSource = source + "!;"
		result = judge.executeProgram(wrongSource, language, stdin, "")
		self.assertEqual(result, status.COMPILE_ERROR)

		wrongSource = self.JAVA_SOURCE_RUNTIME_ERROR
		result = judge.executeProgram(wrongSource, language, stdin, "Foo")
		self.assertEqual(result, status.RUNTIME_ERROR)

	def test_subprocess_judge_python(self):
		source = self.PYTHON_SOURCE
		language = languages.PYTHON
		stdin = ""
		expectedOutputs = [self.HELLO_WORLD, "!!"]
		expectedResults = [status.ANSWER_CORRECT, status.WRONG_ANSWER]

		for i in range(len(expectedOutputs)):
			result = judge.subprocessJudge(source, language, stdin, expectedOutputs[i])
			self.assertEqual(result, expectedResults[i])

		wrongSource = "foo"
		result = judge.subprocessJudge(wrongSource, language, stdin, "")
		self.assertEqual(result, status.RUNTIME_ERROR)

		infiniteSource = "while True: pass"
		result = judge.subprocessJudge(infiniteSource, language, stdin, "")
		self.assertEqual(result, status.TIME_LIMIT_EXCEEDED)

	def test_subprocess_judge_java(self):
		source = self.JAVA_SOURCE
		language = languages.JAVA
		stdin = ""
		expectedOutputs = [self.HELLO_WORLD, "!!"]
		expectedResults = [status.ANSWER_CORRECT, status.WRONG_ANSWER]
		
		for i in range(len(expectedOutputs)):
			result = judge.subprocessJudge(source, language, stdin, expectedOutputs[i])
			self.assertEqual(result, expectedResults[i])

		wrongSource = source + "!;"
		result = judge.subprocessJudge(wrongSource, language, stdin, "")
		self.assertEqual(result, status.COMPILE_ERROR)

		wrongSource = self.JAVA_SOURCE_RUNTIME_ERROR
		result = judge.subprocessJudge(wrongSource, language, stdin, "Foo")
		self.assertEqual(result, status.RUNTIME_ERROR)