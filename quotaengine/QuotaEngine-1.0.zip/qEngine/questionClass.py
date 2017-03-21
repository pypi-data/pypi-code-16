# class Question():
# 	def __init__(self, qData):
# 		self.layer = 0
# 		self.parent = None
#
# 		self.name = qData[1]
#
# 		self.fullName = '_'.join([self.name,self.position])
# 		self.categories = dict()
#
# 	def addCategory(self, catData):
# 		if catData[1] not in self.categories:
# 			self.categories.update({catData[1] : Category(catData)})
#
# 	def setLayer(self,layer):
# 		self.layer = layer
#
# 	def setParent(self,parent):
# 		self.parent = parent
#
# 	@property
# 	def getCategoryNames(self):
# 		# return [x for (y, x) in sorted(zip(self.getCategoryIndexes, [self.categories[i].name for i in self.categories]))]
# 		return [n for (i,n) in sorted([(self.categories[c].index,self.categories[c].name) for c in self.categories])]
#
# 	@property
# 	def getCategoryIndexes(self):
# 		return sorted([self.categories[i].index for i in self.categories])
#
# class Category(Question):
# 	def __init__(self, catData):
# 		self.index = catData[0]
# 		self.name = catData[1]
# 		# print('Category::  %s:%s' % (self.index, self.name))

class Question():
	def __init__(self, name, layer, orderOfAppearence=0):
		self.name = name
		self.layer = layer
		self.orderOfAppearence = orderOfAppearence
		self.categories = dict()
		self.parents = []
		self.children = []

	def addCategory(self, catData):
		if catData[1] not in self.categories:
			self.categories.update({catData[1] : Category(catData)})

	# def setLayer(self,layer):
	# 	self.layer = layer

	# def setParent(self,parent):
	# 	self.parent = parent

	def findByName(self, name):
		for i in self.quotaGroups:
			if i.name == name:
				return i
		raise KeyError(name + ' is not in question ' + self.name)

	def __getitem__(self, key):
		for i in self.categories:
			if self.categories[i].name == key:
				return i
		raise KeyError(key + ' is not in question ' + self.name)

	def __iter__(self):
		return self.categories

	@property
	def child(self):
		try:
			return self.children[0]
		except IndexError:
			return

	@property
	def getCategoryNames(self):
		# return [x for (y, x) in sorted(zip(self.getCategoryIndexes, [self.categories[i].name for i in self.categories]))]
		return [n for (i,n) in sorted([(self.categories[c].index,self.categories[c].name) for c in self.categories])]

	@property
	def getCategoryIndexes(self):
		return sorted([self.categories[i].index for i in self.categories])

class Category():
	def __init__(self, catData):
		self.index = int(catData[0])
		self.name = catData[1]
		# print('Category::  %s:%s' % (self.index, self.name))