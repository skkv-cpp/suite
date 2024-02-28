from typing import List, Union

from suite import config
from suite import asserts
from suite import tests
from suite import results

# Testers.

class Tester:
	def __init__(self, category: str, filename: str, ctor: 'Tester'):
		self.category = category
		self.filename = filename
		self.tests = []
		self.ctor = ctor

	def run(self):
		result: List[results.TestResult] = []
		print("=> Test suite: %s tests." % self.category)
		for i, test in enumerate(self.tests):
			try:
				name = test.name
				if name:
					print("==> Running test \"%s\"" % (name))
				else:
					name = str(i + 1)
					print("==> Running test %d" % (i + 1))
				test_result: results.TestResult = test.run(self.filename)
				if test_result.passed:
					print("===> SUCCESS")
				else:
					print("===> FAILED")
					print("====> ERROR:", test_result.error_message)
				result.append(test_result)
			except Exception as err:
				print("===> FAILED WITH UNKNOWN ERROR. ABORTING...")
				print(err)
				exit(config.EXIT_FAILURE)
		return results.CategoryResult(result, self.category)

	def add_fail(self, input: Union[List[str], str], expected_exitcode: int, timeout: int = config.DEFAULT_TIMEOUT, name: str = None):
		self.add_easy(input, None, expected_exitcode, timeout, name)

	def add_easy(self, input: Union[List[str], str], expected: str, expected_exitcode: int = 0, timeout: int = config.DEFAULT_TIMEOUT, name: str = None):
		expected = asserts.Expected(expected, is_success = expected != None, exitcode = expected_exitcode)
		self.tests.append(self.ctor(input, expected, timeout, name))

	def add_hard(self, input: Union[List[str], str], expected: str, expected_exitcode: int = 0, timeout: int = config.DEFAULT_TIMEOUT, name: str = None):
		expected = asserts.Expected(expected, is_sha256 = True, exitcode = expected_exitcode)
		self.tests.append(self.ctor(input, expected, timeout, name))

class IOTester(Tester):
	def __init__(self, category: str, filename: str):
		Tester.__init__(self, category, filename, tests.IOTest)

class CmdTester(Tester):
	def __init__(self, category: str, filename: str):
		Tester.__init__(self, category, filename, tests.CmdTest)

class MegaTester():
	def __init__(self):
		self.testers: List[Tester] = []

	def add_tester(self, tester: Tester):
		self.testers.append(tester)

	def run(self):
		categories = []
		for tester in self.testers:
			categories.append(tester.run())
		return results.TesterResult(categories)
