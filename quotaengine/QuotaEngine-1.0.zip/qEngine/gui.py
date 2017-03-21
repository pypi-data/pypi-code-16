from PyQt5 import QtWidgets, QtCore
import sys
from quotaSoupClass import quotaSoup
from tabWidgetClass import tabWidget


class quotaGUI(QtWidgets.QMainWindow):
	def __init__(self, *args):
		super().__init__()
		self.defaultState()

		self.centralWidget = QtWidgets.QWidget(self)
		self.initLayout()
		try:
			self.filePath = args[0][1]
			print('Openning %s...' % self.filePath)
			self.loadMQD()
		except IndexError:
			pass

	@property
	def app(self):
		return self._app

	@app.setter
	def app(self, obj):
		self._app = obj


	def defaultState(self):
		self.setWindowTitle('AD Quota Engine')
		self.resize(500, 20)
		self.loaded = False
		self.saved = True
		self.filePath = None

	def initLayout(self):
		self.mainLayout = QtWidgets.QGridLayout(self.centralWidget)
		self.initButtons()
		self.setCentralWidget(self.centralWidget)
		# self.loadMQD() #HERE IS IT!!!!

	def initTabWidget(self):
		self.tabWidget = tabWidget(self.centralWidget, 'South')
		for i in self.qData.quotaGroups:
			self.tabWidget.addNewTab(i)

		self.mainLayout.addWidget(self.tabWidget, 0, 0, 1, 10)
		if self.height() < 500:
			self.resize(self.width(), 500)

	def initButtons(self):
		self.loadBtn = QtWidgets.QPushButton(self.centralWidget)
		self.setOpenBtn(self.loadBtn)
		self.mainLayout.addWidget(self.loadBtn, 1, 9, 1, 1)


		# self.testBtn = QtWidgets.QPushButton(self.centralWidget)
		# self.mainLayout.addWidget(self.testBtn, 1, 2, 1, 1)
		# # self.testBtn.clicked.connect(self.putInClip)
		# self.testBtn.clicked.connect(self.pasteFromClip)
		# self.testBtn.setText('&Test')

	# def checkOneRangeSelected(self, activeTable):
	# 	if len(activeTable.selectedRanges()) != 1:
	# 		if len(activeTable.selectedRanges()) > 1:
	# 			QtWidgets.QMessageBox.critical(self,
	# 			                               'Range Error',
	# 			                               'Cannot be used on multiple ranges',
	# 			                               QtWidgets.QMessageBox.Ok,
	# 			                               QtWidgets.QMessageBox.Ok)
	# 			return False
	# 	return True

	def keyPressEvent(self, e):
		if e.modifiers() == QtCore.Qt.ControlModifier:
			if e.key() == QtCore.Qt.Key_C:
				self.putInClip()
			elif e.key() == QtCore.Qt.Key_V:
				self.pasteFromClip()
			elif e.key() == QtCore.Qt.Key_S:
				self.saveChanges()
		if e.key() == QtCore.Qt.Key_Delete:
			#self.tabWidget.currentWidget().tableWidget.item(i.row(), i.column())
			[i.setText('') for i in self.tabWidget.currentWidget().tableWidget.selectedItems()]


	def getClipData(self, activeTable):
		# structured = lambda lst,nCols: [lst[i:i + nCols] for i in range(0, len(lst), nCols)]
		structured = lambda lst, nCols: '\n'.join(['\t'.join(lst[i:i + nCols]) for i in range(0, len(lst), nCols)])

		# if not self.checkOneRangeSelected(activeTable):
		if not activeTable.oneRangeSelected:
			return
		#
		lst = [i.text() for i in activeTable.tableWidget.selectedItems()]
		# print(lst)
		# print(activeTable.selectedRanges()[0].columnCount())
		# print(structured(lst,activeTable.selectedRanges()[0].columnCount()))
		# print('range: ', [i for i in activeTable.selectedRanges()])
		return structured(lst,activeTable.tableWidget.selectedRanges()[0].columnCount())
		# print('indexes: ', [i for i in activeTable.selectedIndexes()])


	def putInClip(self):
		txt = self.getClipData(self.tabWidget.currentWidget())
		# print(txt)
		if txt:
			self._app.clipboard().setText(txt)

	def pasteFromClip(self):
		activeTable = self.tabWidget.currentWidget()
		# print('topRow: %s, topCol: %s' % (activeTable.selectedRanges()[0].topRow(),activeTable.selectedRanges()[0].leftColumn()))
		# if not self.checkOneRangeSelected(activeTable):
		# 	return
		# print(activeTable.selectedRanges()[0])
		activeTable.insertData([i.split('\t') for i in self._app.clipboard().text().strip().split('\n')],
		                                          startRow=activeTable.tableWidget.selectedRanges()[0].topRow(),
		                                          startColumn=activeTable.tableWidget.selectedRanges()[0].leftColumn())

	def saveChanges(self):
		# print('TBD: Saves Changes')
		for tab in self.tabWidget.tabs:
			tabData = []
			for r in range(tab.tableWidget.rowCount()):
				for c in range(tab.tableWidget.columnCount()):
					cell = tab.tableWidget.item(r,c)
					if cell is None:
						tabData.append('-1')
					elif cell.text() == '':
						tabData.append('-1')
					else:
						tabData.append(cell.text())

			for i,j in zip(self.qData[tab.name].quotaDefs,tabData):
				# if i.target.string != j:
				# 	print(i.target.string,j)
				# 	print(i)

				if j.lower() == 'c':
					# print('counter')
					i.target.string = '0'
					i.flag.string = '2'
				# elif j.lower() == 'o':
				# 	print('over quota')
				else:
					try:
						int(j)
					except ValueError:
						# print(tabData)
						QtWidgets.QMessageBox.critical(self,
						                               'Value Error',
						                               'Check some value error: %s is not an integer' % j,
						                               QtWidgets.QMessageBox.Ok,
						                               QtWidgets.QMessageBox.Ok)
						return
					i.flag.string = '0'
					i.target.string = j


		# savePath = os.path.join(os.path.split(self.filePath)[0], self.newProjectName.text() + '.mqd')
		if self.qData.projectName != self.newProjectName.text():
			savePath = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Quota file', self.newProjectName.text(), '*.mqd')[0].strip('.mqd') + '.mqd'
		else:
			savePath = self.filePath
		print('new save path: %s' % savePath)
		if not savePath:
			return
		with open(savePath,'w') as quotaOut:
			if self.qData.projectName != self.newProjectName.text():
				quotaOut.write(str(self.qData.soup.html.body.xml).replace(self.qData.projectName, self.newProjectName.text()))

				self.filePath = savePath
				self.saved = True

				self.qData = quotaSoup(self.filePath)
				self.setWindowTitle(self.qData.projectName)

			else:
				quotaOut.write(str(self.qData.soup.html.body.xml))

		self.saved = True
		for i in self.tabWidget.tabs:
			i.saved = True

		QtWidgets.QMessageBox.information(self,'Done','Save Success!',QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
		print('Save Success!')

	def setOpenBtn(self, btn):
		try:
			btn.disconnect()
		except TypeError:
			pass
		btn.setText('&Open')
		btn.clicked.connect(self.loadMQD)

	def setCloseBtn(self, btn):
		btn.disconnect()
		btn.setText('&Close')
		btn.clicked.connect(self.closeMQD)

	def loadMQD(self):
		try:
			if not self.filePath:
				self.filePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Quota file', '', '*.mqd')[0]
			# self.filePath = 'YT17deskM1ru.mqd'
			# print(os.path.split(self.filePath))
			# print(os.getcwd())
			self.qData = quotaSoup(self.filePath)
		except FileNotFoundError:
			print('File %s not found' % self.filePath)
			self.defaultState()
			return

		self.setWindowTitle(self.qData.projectName + ' :: Quotas')

		self.saveBtn = QtWidgets.QPushButton('&Save', self.centralWidget)
		self.saveBtn.clicked.connect(self.saveChanges)

		self.newProjectNameLabel = QtWidgets.QLabel('New projectName:', self.centralWidget)
		self.newProjectName = QtWidgets.QLineEdit(self.qData.projectName, self.centralWidget)
		self.newProjectName.setAlignment(QtCore.Qt.AlignVCenter)

		self.mainLayout.addWidget(self.saveBtn, 1, 0, 1, 6)
		self.mainLayout.addWidget(self.newProjectNameLabel, 1, 6, 1, 1)
		self.mainLayout.addWidget(self.newProjectName, 1, 7, 1, 2)

		self.initTabWidget()

		self.loaded = True

		self.setCloseBtn(self.loadBtn)

	def getSaveState(self):
		for i in self.tabWidget.tabs:
			if not i.saved:
				self.saved = False
				return

	def closeMQD(self):
		self.getSaveState()
		if not self.saved:
			if QtWidgets.QMessageBox.question(
				self,
				'Save changes?',
				'Your changes have not been saved. Continue?\n*All changes will be lost',
				QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
				QtWidgets.QMessageBox.Cancel
			) == QtWidgets.QMessageBox.Cancel:
				return

		self.tabWidget.deleteLater()
		self.saveBtn.disconnect()
		self.saveBtn.deleteLater()
		self.newProjectNameLabel.deleteLater()
		self.newProjectName.deleteLater()

		self.setOpenBtn(self.loadBtn)
		self.defaultState()

	def initBars(self):
		self.menubar = QtWidgets.QMenuBar(self)
		self.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(self)
		self.setStatusBar(self.statusbar)


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationName('AD Quota Engine')
	form = quotaGUI(sys.argv)
	form.show()
	sys.exit(app.exec_())