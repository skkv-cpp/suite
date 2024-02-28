import hashlib
import difflib

from suite import config
from suite import results

# Asserts.

class Expected:
	def __init__(self, stdout: str = None, stderr: str = None, is_success: bool = True, is_sha256: bool = False, exitcode: int = 0):
		self.stdout = stdout
		if stdout and not is_sha256 and not stdout.endswith("\n"):
			self.stdout += "\n"
		self.stderr = stderr
		self.is_success = is_success
		self.is_sha256 = is_sha256
		self.exitcode = exitcode

	def compare(self, other: 'Expected', timer: int, name: str, stdin: str) -> results.TestResult:
		expected_stdout = self.stdout
		expected_success = self.is_success
		expected_sha256 = self.is_sha256
		expected_exitcode = self.exitcode
		actual_stdout = other.stdout
		actual_success = other.is_success
		actual_stderr = other.stderr
		actual_exitcode = other.exitcode

		if not expected_success and actual_success:
			return results.TestResult(False, name, expected_success, stdin, actual_stdout, expected_stdout, expected_success != True, timer, "Program returns ERROR_CODE = 0.")

		if expected_success and not actual_success:
			return results.TestResult(False, name,
                              expected_success, stdin, actual_stdout,
                              expected_stdout, expected_success != True,
                              timer, actual_exitcode,
                              "Program should not fail, returns ERROR_CODE != 0."
                )

		if not expected_success:
			if actual_stderr == None or actual_stderr == "":
				return results.TestResult(False, name,
                            expected_success, stdin, actual_stdout,
                            expected_stdout, expected_success != True,
                            timer, actual_exitcode,
                            "Standard error output is empty."
                )
			if actual_stdout != None and actual_stdout != "":
				return results.TestResult(False, name,
                              expected_success, stdin, actual_stdout,
                              expected_stdout, expected_success != True,
                              timer, actual_exitcode,
                              "On error program should not writing anything to standard output."
                )
			if actual_exitcode != expected_exitcode:
				return results.TestResult(False, name,
                              expected_success, stdin, actual_stdout,
                              expected_stdout, expected_success != True,
                              timer, actual_exitcode,
                              "Program returns %d, but should return %d." % (actual_exitcode, expected_exitcode)
                )
			return results.TestResult(True, name,
                             expected_success, stdin, actual_stdout,
                             expected_stdout, expected_success != True,
                             timer, None
            )

		if expected_sha256:
			actual_stdout = hashlib.sha256(actual_stdout.encode("utf-8")).hexdigest()
			if actual_stdout != expected_stdout:
				return results.TestResult(False, name,
                              expected_success, stdin, actual_stdout,
                              expected_stdout, expected_success != True,
                              timer, actual_exitcode,
                              "SHA-256 from expected output (%s) not equals to actual (%s)." % (expected_stdout, actual_stdout)
                )
			else:
				return results.TestResult(True, name,
                              expected_success, stdin, actual_stdout,
                              expected_stdout, expected_success != True,
                              timer, actual_exitcode, None
                )

		if actual_stdout != expected_stdout:
			diff = difflib.unified_diff(expected_stdout.splitlines(), 
										 actual_stdout.splitlines(), 
										 fromfile = 'expected_stdout', 
										 tofile = 'actual_stdout')
			ndiff = '\n'.join(diff)
			return results.TestResult(False, name,
                              expected_success, stdin, actual_stdout,
                              expected_stdout, expected_success != True,
                              timer, actual_exitcode,
                              "Expected:\n\"\"\"\n%s\"\"\"\nbut actual is:\n\"\"\"\n%s\"\"\"Difference (https://docs.python.org/3/library/difflib.html#difflib.unified_diff): \n%s\n" %  (expected_stdout, actual_stdout, ndiff)
                )

		return results.TestResult(True, name, expected_success, stdin, actual_stdout, expected_stdout, expected_success != True, timer, actual_exitcode, None)

class Actual(Expected):
	def __init__(self, stdout: str, stderr: str, exitcode: int):
		Expected.__init__(self, stdout = stdout, stderr = stderr, is_success = (exitcode == config.EXIT_SUCCESS), exitcode = exitcode)
