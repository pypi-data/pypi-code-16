# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Fri Feb  3 10:05:49 2017
#      by: PyQt4 UI code generator 4.10.4
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
        MainWindow.setEnabled(True)
        MainWindow.resize(658, 482)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.layoutWidget_3 = QtGui.QWidget(self.centralwidget)
        self.layoutWidget_3.setGeometry(QtCore.QRect(10, -30, 701, 28))
        self.layoutWidget_3.setObjectName(_fromUtf8("layoutWidget_3"))
        self.gridLayout_7 = QtGui.QGridLayout(self.layoutWidget_3)
        self.gridLayout_7.setMargin(0)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.line_2 = QtGui.QFrame(self.layoutWidget_3)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout_7.addWidget(self.line_2, 2, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.layoutWidget_3)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_7.addWidget(self.label_16, 1, 0, 1, 1)
        self.pushButton_RunSeePy = QtGui.QPushButton(self.centralwidget)
        self.pushButton_RunSeePy.setGeometry(QtCore.QRect(20, 390, 81, 23))
        self.pushButton_RunSeePy.setObjectName(_fromUtf8("pushButton_RunSeePy"))
        self.listWidget_ScriptsList = QtGui.QListWidget(self.centralwidget)
        self.listWidget_ScriptsList.setGeometry(QtCore.QRect(20, 60, 231, 321))
        self.listWidget_ScriptsList.setObjectName(_fromUtf8("listWidget_ScriptsList"))
        self.pushButton_RunSelectedScript = QtGui.QPushButton(self.centralwidget)
        self.pushButton_RunSelectedScript.setGeometry(QtCore.QRect(110, 390, 141, 23))
        self.pushButton_RunSelectedScript.setObjectName(_fromUtf8("pushButton_RunSelectedScript"))
        self.textBrowser_ScriptDescription = QtGui.QTextBrowser(self.centralwidget)
        self.textBrowser_ScriptDescription.setGeometry(QtCore.QRect(280, 20, 361, 391))
        self.textBrowser_ScriptDescription.setObjectName(_fromUtf8("textBrowser_ScriptDescription"))
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(20, 20, 231, 27))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 658, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu_2 = QtGui.QMenu(self.menubar)
        self.menuMenu_2.setObjectName(_fromUtf8("menuMenu_2"))
        MainWindow.setMenuBar(self.menubar)
        self.actionAbout_STRUTHON_CENCRERE_MONO = QtGui.QAction(MainWindow)
        self.actionAbout_STRUTHON_CENCRERE_MONO.setObjectName(_fromUtf8("actionAbout_STRUTHON_CENCRERE_MONO"))
        self.actionAdd_dir = QtGui.QAction(MainWindow)
        self.actionAdd_dir.setObjectName(_fromUtf8("actionAdd_dir"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuMenu_2.addSeparator()
        self.menuMenu_2.addAction(self.actionAbout)
        self.menubar.addAction(self.menuMenu_2.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Py4Structure", None))
        self.label_16.setText(_translate("MainWindow", "Section properties", None))
        self.pushButton_RunSeePy.setText(_translate("MainWindow", "Run SeePy", None))
        self.pushButton_RunSelectedScript.setText(_translate("MainWindow", "Run Selected Script", None))
        self.menuMenu_2.setTitle(_translate("MainWindow", "...", None))
        self.actionAbout_STRUTHON_CENCRERE_MONO.setText(_translate("MainWindow", "About STRUTHON CENCRERE MONO", None))
        self.actionAdd_dir.setText(_translate("MainWindow", "Add dir", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))

