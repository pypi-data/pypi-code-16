
__version__ = '0.1'

class lmatrix:

	def __init__(self, m, n, value=0, init=True):
		if init:
			self.rows = [[value]*n for x in range(m)]
		else:
			self.rows = []
		self.m = m
		self.n =n

	def __getitem__(self, idx):
		if type(idx) == tuple:
			return self.rows[idx[0]][idx[1]]
		return self.rows[idx]

	def __setitem__(self, idx, value):
		if type(idx) == tuple:
			self.rows[idx[0]][idx[1]] = value
		else:
			self.rows[idx] = value

	def __str__(self):
		s = '\n'.join(' '.join([str(item) for item in row]) for row in self.rows)
		return s

	def __eq__(self, mat):
		return (mat.rows == self.rows)
	
