import os
import subprocess

from suite import config
from suite import asserts

# Tests.

class IOTest:
	def __init__(self, input, expected_result, timeout = config.DEFAULT_TIMEOUT, name = None):
		self.input = (' '.join(input) + "\n").encode("ascii")
		self.expected_result = expected_result
		self.timeout = timeout
		self.name = name

	def run(self, filename):
		executable = os.path.abspath(filename)
		program = subprocess.Popen([executable], stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
		try:
			output, error = program.communicate(self.input.decode("utf-8"), timeout = self.timeout)
			result = asserts.Actual(output, error, program.returncode)
			self.expected_result.compare(result)
		except ValueError as err:
			raise err
		except subprocess.TimeoutExpired:
			raise ValueError("Timeout.")

	def about(self):
		return self.name

class CmdTest:
	def __init__(self, input, expected_result, timeout = config.DEFAULT_TIMEOUT, name = None):
		self.input = input
		self.expected_result = expected_result
		self.timeout = timeout
		self.name = name

	def run(self, filename):
		executable = os.path.abspath(filename)
		program = subprocess.Popen([executable] + self.input, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
		try:
			output, error = program.communicate(timeout = self.timeout)
			result = asserts.Actual(output, error, program.returncode)
			self.expected_result.compare(result)
		except ValueError as err:
			raise err
		except subprocess.TimeoutExpired:
			raise ValueError("Timeout.")

	def about(self):
		return self.name