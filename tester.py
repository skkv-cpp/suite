import time

from suite import config
from suite import asserts
from suite import tests
from suite import results

# Testers.

class Tester:
	def __init__(self, name, filename, ctor):
		self.groupname = name
		self.filename = filename
		self.tests = []
		self.ctor = ctor

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
		return results.GroupResult(passed, len(self.tests), self.groupname, end - start)

	def add_fail(self, input, timeout = config.DEFAULT_TIMEOUT, name = None):
		self.add_easy(input, None, timeout, name)

	def add_easy(self, input, expected, timeout = config.DEFAULT_TIMEOUT, name = None):
		expected = asserts.Expected(expected, is_success = expected != None)
		self.tests.append(self.ctor(input, expected, timeout, name))

	def add_hard(self, input, expected, timeout = config.DEFAULT_TIMEOUT, name = None):
		expected = asserts.Expected(expected, is_sha256 = True)
		self.tests.append(self.ctor(input, expected, timeout, name))

class IOTester(Tester):
	def __init__(self, name, filename):
		Tester.__init__(self, name, filename, tests.IOTest)

class CmdTester(Tester):
	def __init__(self, name, filename):
		Tester.__init__(self, name, filename, tests.CmdTest)
