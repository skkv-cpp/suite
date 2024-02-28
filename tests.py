import os
import subprocess
import time

from suite import config
from suite import asserts
from suite import results

# Tests.

class IOTest:
	def __init__(self, input, expected_result: asserts.Expected, timeout: int = config.DEFAULT_TIMEOUT, name: str = None):
		self.input = (' '.join(input) + "\n").encode("ascii")
		self.expected_result = expected_result
		self.timeout: int = timeout
		self.name: str = name

	def run(self, filename: str):
		executable = os.path.abspath(filename)
		start = time.time_ns() // 1000000
		program = subprocess.Popen([executable], stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
		try:
			output, error = program.communicate(self.input.decode("utf-8"), timeout = self.timeout)
			end = time.time_ns() // 1000000
			result = asserts.Actual(output, error, program.returncode)
			return self.expected_result.compare(result, end - start, self.name, self.input)
		except subprocess.TimeoutExpired:
			end = time.time_ns() // 1000000
			return results.TestResult(False, self.name, self.expected_result.is_success, self.input, None, self.expected_result.stdout, self.expected_result.is_success != True, end - start, "Timeout.")

class CmdTest:
	def __init__(self, input, expected_result: asserts.Expected, timeout: int = config.DEFAULT_TIMEOUT, name: str = None):
		self.input = input
		self.expected_result = expected_result
		self.timeout = timeout
		self.name = name

	def run(self, filename: str):
		executable = os.path.abspath(filename)
		start = time.time_ns() // 1000000
		program = subprocess.Popen([executable] + self.input, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
		try:
			output, error = program.communicate(timeout = self.timeout)
			end = time.time_ns() // 1000000
			result = asserts.Actual(output, error, program.returncode)
			return self.expected_result.compare(result, end - start, self.name, self.input)
		except subprocess.TimeoutExpired:
			end = time.time_ns() // 1000000
			return results.TestResult(False, self.name, self.expected_result.is_success, self.input, None, self.expected_result.stdout, self.expected_result.is_success != True, end - start, "Timeout.")
