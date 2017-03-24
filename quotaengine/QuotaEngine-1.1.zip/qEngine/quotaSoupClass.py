from bs4 import BeautifulSoup
from quotaGroupClass import qoutaGroup

class quotaSoup():
	def __init__(self, filePath):
		self.filePath = filePath
		self.rawText = open(self.filePath,'r').read()
		self.soup = BeautifulSoup(self.rawText,'lxml')
		self.projectName = self.soup.find('xml').find('xml')['name']
		self.quotaGroups = self.getQuotaGroups()
		self.setQuotaGroupsDescriptors()


	def getQuotaGroups(self):
		result = []
		for i in self.soup.findAll('mrquota:quotagroup'):
			if ':Expressions"' not in str(i):
				result.append(qoutaGroup(i))
		return result

	def setQuotaGroupsDescriptors(self):
		# print([i['name'] for i in self.soup.findAll('mrtom:table')])
		for i in self.soup.findAll('mrtom:table'):
			# print(i['name'].split(':')[1])
			self[i['name'].split(':')[1]].setDescriptor(i)
			# result.append(qoutaGroup(i))

	def findByName(self, name):
		for i in self.quotaGroups:
			if i.name == name:
				return i
		raise KeyError(name + ' is not in quota tables')

	def __getitem__(self, key):
		return self.findByName(key)

	def __iter__(self):
		return iter(self.quotaGroups)

	def __len__(self):
		return len(self.quotaGroups)
