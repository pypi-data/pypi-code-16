# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 630)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuExport = QtGui.QMenu(self.menuBar)
        self.menuExport.setObjectName(_fromUtf8("menuExport"))
        self.menuData = QtGui.QMenu(self.menuBar)
        self.menuData.setObjectName(_fromUtf8("menuData"))
        MainWindow.setMenuBar(self.menuBar)
        self.actNewplot = QtGui.QAction(MainWindow)
        self.actNewplot.setObjectName(_fromUtf8("actNewplot"))
        self.actQuit = QtGui.QAction(MainWindow)
        self.actQuit.setObjectName(_fromUtf8("actQuit"))
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuData.menuAction())
        self.menuBar.addAction(self.menuExport.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "GraPhysio", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuExport.setTitle(_translate("MainWindow", "Export", None))
        self.menuData.setTitle(_translate("MainWindow", "Data", None))
        self.actNewplot.setText(_translate("MainWindow", "New plot", None))
        self.actQuit.setText(_translate("MainWindow", "Quit", None))

