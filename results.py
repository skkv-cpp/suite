# Results.

class GroupResult():
	def __init__(self, passed, total, name, timer):
		self.passed = passed
		self.total = total
		self.name = name
		self.timer = timer

	def __str__(self):
		return "Group %s: %d/%d tests passed in %d ms" % (self.name, self.passed, self.total, self.timer)
