import subprocess
import hashlib
import os
import difflib
import time

# Constants.

EXIT_SUCCESS = 0
EXIT_FAILURE = -1
DEFAULT_TIMEOUT = 1

# Classes.

## Results.

class ExpectedResult:
	def __init__(self, stdout = None, stderr = None, is_success = True, is_sha256 = False):
		self.stdout = stdout
		if stdout and not is_sha256 and not stdout.endswith("\n"):
			self.stdout += "\n"
		self.stderr = stderr
		self.is_success = is_success
		self.is_sha256 = is_sha256

	def compare(self, other):
		expected_stdout = self.stdout
		expected_success = self.is_success
		expected_sha256 = self.is_sha256
		actual_stdout = other.stdout
		actual_success = other.is_success
		actual_stderr = other.stderr

		if not expected_success and actual_success:
			raise ValueError("Program returns ERROR_CODE = 0.")

		if expected_success and not actual_success:
			raise ValueError("Program should not fail, returns ERROR_CODE != 0.")

		if not expected_success:
			if actual_stderr == None or actual_stderr == "":
				raise ValueError("Standard error output is empty.")
			if actual_stdout != None and actual_stdout != "":
				raise ValueError("On error program should not writing anything to standard output.")
			return

		if expected_sha256:
			actual_stdout = hashlib.sha256(actual_stdout.encode("utf-8")).hexdigest()
			if actual_stdout != expected_stdout:
				raise ValueError("SHA-256 from expected output (%s) not equals to actual (%s)." % (expected_stdout, actual_stdout))
			else:
				return

		if actual_stdout != expected_stdout:
			diff = difflib.unified_diff(expected_stdout.splitlines(), 
										 actual_stdout.splitlines(), 
										 fromfile = 'expected_stdout', 
										 tofile = 'actual_stdout')
			ndiff = '\n'.join(diff)
			raise ValueError("Expected:\n\"\"\"\n%s\"\"\"\nbut actual is:\n\"\"\"\n%s\"\"\"Difference (https://docs.python.org/3/library/difflib.html#difflib.unified_diff): \n%s\n" % 
								(expected_stdout, actual_stdout, ndiff))

class TestResult(ExpectedResult):
	def __init__(self, stdout, stderr, return_code):
		ExpectedResult.__init__(self, stdout = stdout, stderr = stderr, is_success = (return_code == EXIT_SUCCESS))

class GroupResult():
	def __init__(self, passed, total, name, timer):
		self.passed = passed
		self.total = total
		self.name = name
		self.timer = timer

	def __str__(self):
		return "Group %s: %d/%d tests passed in %d ms" % (self.name, self.passed, self.total, self.timer)

## Tests.

class IOTest:
	def __init__(self, input, expected_result, timeout = DEFAULT_TIMEOUT, name = None):
		self.input = (' '.join(input) + "\n").encode("ascii")
		self.expected_result = expected_result
		self.timeout = timeout
		self.name = name

	def run(self, filename):
		executable = os.path.abspath(filename)
		program = subprocess.Popen([executable], stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
		try:
			output, error = program.communicate(self.input.decode("utf-8"), timeout = self.timeout)
			result = TestResult(output, error, program.returncode)
			self.expected_result.compare(result)
		except ValueError as err:
			raise err
		except subprocess.TimeoutExpired:
			raise ValueError("Timeout.")

	def about(self):
		return self.name

class CmdTest:
	def __init__(self, input, expected_result, timeout = DEFAULT_TIMEOUT, name = None):
		self.input = input
		self.expected_result = expected_result
		self.timeout = timeout
		self.name = name

	def run(self, filename):
		executable = os.path.abspath(filename)
		program = subprocess.Popen([executable] + self.input, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
		try:
			output, error = program.communicate(timeout = self.timeout)
			result = TestResult(output, error, program.returncode)
			self.expected_result.compare(result)
		except ValueError as err:
			raise err
		except subprocess.TimeoutExpired:
			raise ValueError("Timeout.")

	def about(self):
		return self.name

## Testers.

class IOTester:
	def __init__(self, name, filename):
		self.groupname = name
		self.filename = filename
		self.tests = []

	def run(self):
		passed = 0
		start = time.time_ns() // 1000000
		print("=> Test suite: %s tests." % self.groupname)
		for i, test in enumerate(self.tests):
			try:
				name = test.about()
				if name:
					print("==> Running test \"%s\"" % (name))
				else:
					print("==> Running test %d" % (i + 1))
				test.run(self.filename)
				print("===> SUCCESS")
				passed += 1
			except ValueError as err:
				print("===> FAILED")
				print("====> ERROR:", err)
			except Exception as err:
				print("===> FAILED WITH UNKNOWN ERROR")
				print(err)
		end = time.time_ns() // 1000000
		return GroupResult(passed, len(self.tests), self.groupname, end - start)

	def add_fail(self, input, timeout = DEFAULT_TIMEOUT, name = None):
		self.add_easy(input, None, timeout, name)

	def add_easy(self, input, expected, timeout = DEFAULT_TIMEOUT, name = None):
		expected = ExpectedResult(expected, is_success = expected != None)
		self.tests.append(IOTest(input, expected, timeout, name))

	def add_hard(self, input, expected, timeout = DEFAULT_TIMEOUT, name = None):
		expected = ExpectedResult(expected, is_sha256 = True)
		self.tests.append(IOTest(input, expected, timeout, name))

class CmdTester:
	def __init__(self, name, filename):
		self.groupname = name
		self.filename = filename
		self.tests = []

	def run(self):
		passed = 0
		start = time.time_ns() // 1000000
		print("=> Test suite: %s tests." % self.groupname)
		for i, test in enumerate(self.tests):
			try:
				name = test.about()
				if name:
					print("==> Running test \"%s\"" % (name))
				else:
					print("==> Running test %d" % (i + 1))
				test.run(self.filename)
				print("===> SUCCESS")
				passed += 1
			except ValueError as err:
				print("===> FAILED")
				print("====> ERROR:", err)
			except Exception as err:
				print("===> FAILED WITH UNKNOWN ERROR")
				print(err)
		end = time.time_ns() // 1000000
		return GroupResult(passed, len(self.tests), self.groupname, end - start)

	def add_fail(self, input, timeout = DEFAULT_TIMEOUT, name = None):
		self.add_easy(input, None, timeout, name)

	def add_easy(self, input, expected, timeout = DEFAULT_TIMEOUT, name = None):
		expected = ExpectedResult(expected, is_success = expected != None)
		self.tests.append(CmdTest(input, expected, timeout, name))

	def add_hard(self, input, expected, timeout = DEFAULT_TIMEOUT, name = None):
		expected = ExpectedResult(expected, is_sha256 = True)
		self.tests.append(CmdTest(input, expected, timeout, name))
