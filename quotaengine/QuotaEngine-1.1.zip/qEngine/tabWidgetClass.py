from PyQt5 import QtWidgets
from tableWidgetClass import tabClass

class tabWidget(QtWidgets.QTabWidget):
	tabPositions = {
		'North': 0,
		'South': 1,
		'West': 2,
		'East': 3
	}

	def __init__(self, parentObject, pos):
		super().__init__(parentObject)
		self.setTabPosition(self.tabPositions[pos])
		self.setTabShape(self.Triangular)
		self.setMovable(True)
		self.tabs = []
		self.setCurrentIndex(0)

	# if super().height() < 500:
	# 	super().setMinimumHeight(500)

	def addNewTab(self, qGroup):
		qGroup.setTab(tabClass(qGroup))
		tab = qGroup.linkedTab
		self.tabs.append(tab)
		self.addTab(tab, tab.name)