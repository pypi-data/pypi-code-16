from PyQt5 import QtWidgets, QtCore
from miscFunctions import combineLists


class tabClass(QtWidgets.QWidget):
	def __init__(self, qGroup):
		super().__init__()
		self.saved = True
		self.qData = qGroup
		self.name = self.qData.name

		# headerarr = []



		# for i in self.qData.topQuestions.keys():
		# 	for j in self.qData.topQuestions[i].getCategoryNames:
		# 		print(self.qData.topQuestions[i].layer, j)

		self.gridLayout = QtWidgets.QGridLayout(self)
		self.topHeader = QtWidgets.QHBoxLayout()
		self.sideHeader = QtWidgets.QVBoxLayout()

		self.tableWidget = QtWidgets.QTableWidget(self)
		self.tableWidget.setRowCount(len(self.qData.targetStructure))
		self.tableWidget.setColumnCount(len(self.qData.targetStructure[0]))

		# if self.name == 'TEST4':
		# print('new table:: %s' % self.name)
		# print(self.tableWidget.verticalHeader())
		self.tableWidget.setHorizontalHeaderLabels(self.getQuotaHeaders('top'))
		self.tableWidget.setVerticalHeaderLabels(self.getQuotaHeaders('side'))

		# print(self.qData.tableStructure)
		self.insertData(self.qData.tableStructure)

		# for r in range(self.tableWidget.rowCount()):
		# 	for c in range(self.tableWidget.columnCount()):
		# 		# print(self.qData.targetStructure[r][c])
		# 		cell = QtWidgets.QTableWidgetItem(str(self.qData.targetStructure[r][c]))
		# 		cell.setTextAlignment(QtCore.Qt.AlignCenter) #132
		# 		self.tableWidget.setItem(r,c,cell)

		self.tableWidget.cellChanged.connect(self.setUnsaved)
		self.tableWidget.horizontalHeader().setDefaultSectionSize(50)
		self.tableWidget.verticalHeader().setDefaultSectionSize(50)
		self.tableWidget.resizeColumnsToContents()
		self.tableWidget.resizeRowsToContents()
		self.tableWidget.setAcceptDrops(True)

		self.gridLayout.addLayout(self.topHeader, 1, 0, 1, 1)
		self.gridLayout.addLayout(self.sideHeader, 0, 1, 1, 1)
		self.gridLayout.addWidget(self.tableWidget, 2, 2, 1, 1)

	def getChildren(self, obj):
		arr = []
		combArr = []
		for i in obj.getCategoryNames:
			arr.append('{ques}:{cat}'.format(ques=obj.name, cat=i))

		if obj.child:
			combArr.append(arr)
			combArr.append(self.getChildren(self.qData.allQuestions[obj.child]))
			return combineLists(combArr)

		# for i in obj.children:
		# 	combArr.append(arr)
		# 	combArr.append(self.getChildren(self.qData.allQuestions[i]))
			# arr = combineLists([arr,self.getChildren(self.qData.allQuestions[i])])
		# if combArr:
		# 	return combineLists(combArr)
		return arr

	def getQuotaHeaders(self, position):
		# print([n for (i, n) in sorted(
		# 	[(self.qData.topQuestions[c].layer, self.qData.topQuestions[c]) for c in
		# 	 self.qData.topQuestions.keys()])][:-1])
		# print(self.qData.topQuestions)
		# print([self.qData.sideQuestions[c].parent for c in self.qData.sideQuestions.keys()])


		quests = {
				'top' : self.qData.topQuestionsSorted,
				'side' : self.qData.sideQuestionsSorted
		        }
		result = []
		# if position == '':
			# for i in [n for (i, n) in
			#           sorted([(self.qData.topQuestions[c].layer, self.qData.topQuestions[c]) for c in
			#                                   self.qData.topQuestions.keys()])]:
			# 	result.append(['%s:%s' % (i.name, j) for j in i.getCategoryNames])
		# 	quests =
		# elif position == '':
		# 	quests =


		for i in quests[position]:
			if i.layer == 0:
			# print(i.getCategoryIndexes)
			# 	print('q: ',i.name)
			# 	print('TEST', self.getChildren(i))
				result = result + self.getChildren(i)
			# print(i.name,[ii.name for ii in i.children])
			# for ii in i.getCategoryNames:
			#
			# 	result.append(['{ques}:{cat}'.format(ques=i.name, cat=ii)])
			# print(result)

		# try:
		# 	for i in [n for (i, n) in
		# 	          sorted([(self.qData.sideQuestions[c].layer, self.qData.sideQuestions[c]) for c in
		# 	                                  self.qData.sideQuestions.keys()])]:
		# 		result.append(['%s:%s' % (i.name, j) for j in i.getCategoryNames])
		# except Exception as inst:
		# 	print('eeeeerrrrr %s' % inst.args)
		# print(result)

		return result

	@property
	def oneRangeSelected(self):
		if len(self.tableWidget.selectedRanges()) != 1:
			if len(self.tableWidget.selectedRanges()) > 1:
				QtWidgets.QMessageBox.critical(self,
				                               'Range Error',
				                               'Cannot be used on multiple ranges',
				                               QtWidgets.QMessageBox.Ok,
				                               QtWidgets.QMessageBox.Ok)
				return False
		return True

	def insertData(self, tableData, startRow = 0, startColumn = 0):


		endRow, endColumn = (startRow + len(tableData), startColumn + len(tableData[0]))
		# print(('startRow: {sr}\trows: {len1}\nstartColumn: {sc}\tcols: {len2}\nendRow: {er}\tendColumn: {ec}').format(
		# 																				sr=startRow,
		#                                                                                 len1=len(tableData),
		#                                                                                 sc=startColumn,
		#                                                                                 len2=len(tableData[0]),
		#                                                                                 er=endRow,
		#                                                                                 ec=endColumn
		#                                                                                ))
		if endRow > self.tableWidget.rowCount() or endColumn > self.tableWidget.columnCount():
			print('WRONG DIMENSIONS')
			return


		if len(tableData) == 1 and len(tableData[0]) == 1:
			# print(tableData)
			for i in self.tableWidget.selectedItems():
				i.setText(tableData[0][0])
		else:
			self.tableWidget.clearSelection()
			for r in range(startRow, endRow):
				for c in range(startColumn, endColumn):
					# print(self.qData.targetStructure[r][c])
					try:
						# print(self.tableWidget.item(r, c).text())

						self.tableWidget.item(r, c).setText(str(tableData[r-startRow][c-startColumn]))


						self.tableWidget.setCurrentCell(r,c)#setCurrentItem(self.tableWidget.item(r, c))


					except AttributeError:
						cell = QtWidgets.QTableWidgetItem(str(tableData[r-startRow][c-startColumn]))
						cell.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tableWidget.setItem(r, c, cell)

	def setUnsaved(self):
		self.saved = False