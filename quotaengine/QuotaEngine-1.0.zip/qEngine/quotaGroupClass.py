import re
from questionClass import Question
from miscFunctions import prod, merge_dicts

class qoutaGroup():
	def __init__(self, groupData):
		# print(groupData)
		self.data = groupData
		self.name = self.data.find('name').string
		self.quotaDefs = self.data.findAll('quota-def')
		self.cellData = [i['name'] for i in self.quotaDefs]
		self.targetArray = [i.target.string for i in self.quotaDefs]
		self.typeArray = [i.flag.string for i in self.quotaDefs]

		# self.topQuestions = None
		# self.sideQuestions = None

	def setDescriptor(self,data):
		self.descriptor = data
		self.side = self.descriptor.find('mrtom:dimension1')
		self.top = self.descriptor.find('mrtom:dimension2')

		self.sideQuestions = self.getQuestions(self.side)
		self.topQuestions = self.getQuestions(self.top)
		self.allQuestions = merge_dicts(self.sideQuestions,self.topQuestions)

		sortedQestion = lambda X: [n for (i, n) in sorted([(X[c].orderOfAppearence, X[c]) for c in X.keys()])]
		self.sideQuestionsSorted = sortedQestion(self.sideQuestions)
		self.topQuestionsSorted = sortedQestion(self.topQuestions)

		self.getQData(self.cellData)

		self.approximateTopCells = prod([len(self.topQuestions[i].categories) for i in self.topQuestions])

		self.targetStructure = self.getStrucutre(self.targetArray, self.approximateTopCells)
		self.typeStructure = self.getStrucutre(self.typeArray, self.approximateTopCells)
		self.tableStructure = self.getStrucutre(self.processDataForTable(), self.approximateTopCells)

	def processDataForTable(self):
		result = []
		for i,j in zip(self.targetArray,self.typeArray):
			if j.lower() == '2':
				result.append('c')
			else:
				result.append(i)
		return result

	def setTab(self, tabObj):
		self.linkedTab = tabObj

	def getStrucutre(self, lst, cols):
		return [lst[i:i + cols] for i in range(0, len(lst), cols)]

	def getQuestions(self, tagString, result=None, layer=0, parent=None, orderOfAppearence=0):
		if not result:
			result = dict()

		for i in tagString.findAll('mrtom:table-element', attrs={'name': re.compile('.')}):
			foundIntended = i.find('mrtom:table-element', attrs={'name': re.compile('.')})

			try:
				qObject = result[i['name']]
			except KeyError:
				qObject = Question(i['name'], layer, orderOfAppearence)
			if parent:
				# parent.children.append(qObject)
				if parent not in qObject.parents:
					qObject.parents.append(parent)
				if i['name'] not in result[parent].children:
					result[parent].children.append(i['name'])
			result.update({i['name']: qObject})
			orderOfAppearence += 1

			if foundIntended:
				layer += 1
				# result = self.getQuestions(foundIntended, result=result, layer=layer, parent=result[i['name']], orderOfAppearence=orderOfAppearence)
				result = self.getQuestions(i, result=result, layer=layer, parent=i['name'],
				                           orderOfAppearence=orderOfAppearence)
			else:
				layer = 0

		return result

	def getQData(self, axisData):
		for i in self.cellData:

			tmp = re.search('Top.+',i)
			if tmp:
				tmp = tmp.span()[0]
			else:
				tmp = len(i)

			sidePart = i[:tmp]
			topPart = i[tmp:]
			if 'Side' in i:
				# print('side: %s' % sidePart)
				self.fillCategories(sidePart, self.sideQuestions)  # inspect if only 1 axis
			if 'Top' in i:
				# print('top: %s' % topPart)
				self.fillCategories(topPart, self.topQuestions)


	def fillCategories(self, axis, questionData):
		patt = '\((.*?)\)'
		axisData = re.findall(patt, axis)
		# print(len(axisData) // 2)
		quesPart = lambda x: axisData[x]
		catPart = lambda x: axisData[x + 1]

		for i in range(0,len(axisData),2):
			qCurrent = questionData[quesPart(i).split('.')[1]]
			# print(qCurrent.name)
			qCurrent.addCategory(catPart(i).split('.'))
			# if ii > 0:
			# 	print(quesPart(ii),'>>',quesPart(ii-1))

	# def checkQues(self, ques):
	# 	if ques.fullName not in self.quests:
	# 		self.quests.update({ques.fullName: ques})
	# 		return ques
	# 	else:
	# 		return self.quests[ques.fullName]

