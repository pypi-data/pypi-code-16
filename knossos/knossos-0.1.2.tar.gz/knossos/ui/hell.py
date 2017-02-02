# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/hell.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(499, 615)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolbar = QtWidgets.QFrame(self.centralwidget)
        self.toolbar.setObjectName("toolbar")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.toolbar)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pageControls = QtWidgets.QWidget(self.toolbar)
        self.pageControls.setObjectName("pageControls")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.pageControls)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.backButton = QtWidgets.QPushButton(self.pageControls)
        self.backButton.setObjectName("backButton")
        self.horizontalLayout_2.addWidget(self.backButton)
        self.horizontalLayout.addWidget(self.pageControls)
        self.listControls = QtWidgets.QWidget(self.toolbar)
        self.listControls.setObjectName("listControls")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.listControls)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.searchEdit = QtWidgets.QLineEdit(self.listControls)
        self.searchEdit.setObjectName("searchEdit")
        self.horizontalLayout_3.addWidget(self.searchEdit)
        self.horizontalLayout.addWidget(self.listControls)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.updateButton = QtWidgets.QPushButton(self.toolbar)
        self.updateButton.setObjectName("updateButton")
        self.horizontalLayout.addWidget(self.updateButton)
        self.settingsButton = QtWidgets.QPushButton(self.toolbar)
        self.settingsButton.setObjectName("settingsButton")
        self.horizontalLayout.addWidget(self.settingsButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.toolbar)
        self.tabButtons = QtWidgets.QWidget(self.centralwidget)
        self.tabButtons.setObjectName("tabButtons")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tabButtons)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.installedButton = QtWidgets.QToolButton(self.tabButtons)
        self.installedButton.setCheckable(True)
        self.installedButton.setAutoRaise(True)
        self.installedButton.setObjectName("installedButton")
        self.horizontalLayout_4.addWidget(self.installedButton)
        self.availableButton = QtWidgets.QToolButton(self.tabButtons)
        self.availableButton.setCheckable(True)
        self.availableButton.setAutoRaise(True)
        self.availableButton.setObjectName("availableButton")
        self.horizontalLayout_4.addWidget(self.availableButton)
        self.updatesButton = QtWidgets.QToolButton(self.tabButtons)
        self.updatesButton.setCheckable(True)
        self.updatesButton.setAutoRaise(True)
        self.updatesButton.setObjectName("updatesButton")
        self.horizontalLayout_4.addWidget(self.updatesButton)
        self.progressButton = QtWidgets.QToolButton(self.tabButtons)
        self.progressButton.setCheckable(True)
        self.progressButton.setAutoRaise(True)
        self.progressButton.setObjectName("progressButton")
        self.horizontalLayout_4.addWidget(self.progressButton)
        self.verticalLayout.addWidget(self.tabButtons)
        self.webView = QtWebKitWidgets.QWebView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.progressInfo = QtWidgets.QWidget(self.centralwidget)
        self.progressInfo.setObjectName("progressInfo")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.progressInfo)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.progressLabel = QtWidgets.QLabel(self.progressInfo)
        self.progressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.progressLabel.setObjectName("progressLabel")
        self.verticalLayout_2.addWidget(self.progressLabel)
        self.progressBar = QtWidgets.QProgressBar(self.progressInfo)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_2.addWidget(self.progressBar)
        self.verticalLayout.addWidget(self.progressInfo)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 499, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Knossos"))
        self.backButton.setText(_translate("MainWindow", "Back"))
        self.searchEdit.setPlaceholderText(_translate("MainWindow", "Search"))
        self.updateButton.setText(_translate("MainWindow", "Update List"))
        self.settingsButton.setText(_translate("MainWindow", "Settings"))
        self.installedButton.setText(_translate("MainWindow", "Installed"))
        self.availableButton.setText(_translate("MainWindow", "Available"))
        self.updatesButton.setText(_translate("MainWindow", "Updates"))
        self.progressButton.setText(_translate("MainWindow", "Progress"))
        self.progressLabel.setText(_translate("MainWindow", "TextLabel"))

from ..qt import QtWebKitWidgets
