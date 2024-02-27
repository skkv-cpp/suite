import hashlib
import difflib

from suite import config

# Asserts.

class Expected:
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

class Actual(Expected):
	def __init__(self, stdout, stderr, return_code):
		Expected.__init__(self, stdout = stdout, stderr = stderr, is_success = (return_code == config.EXIT_SUCCESS))
