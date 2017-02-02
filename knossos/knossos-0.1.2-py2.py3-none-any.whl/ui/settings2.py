# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings2.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(575, 400)
        Dialog.setModal(True)
        self.layout = QtWidgets.QHBoxLayout(Dialog)
        self.layout.setObjectName("layout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.saveButton = QtWidgets.QPushButton(Dialog)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout.addWidget(self.saveButton)
        self.treeWidget = QtWidgets.QTreeWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMaximumSize(QtCore.QSize(149, 16777215))
        self.treeWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeWidget.setProperty("showDropIndicator", False)
        self.treeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.treeWidget.setWordWrap(True)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.topLevelItem(0).setText(0, "About Knossos")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.topLevelItem(1).setText(0, "Launcher settings")
        item_0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(1).child(0).setText(0, "Retail install")
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(1).child(1).setText(0, "Mod sources")
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(1).child(2).setText(0, "Mod versions")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.topLevelItem(2).setText(0, "Game settings")
        item_0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(2).child(0).setText(0, "Video")
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(2).child(1).setText(0, "Audio")
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(2).child(2).setText(0, "Input")
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(2).child(3).setText(0, "Network")
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.topLevelItem(2).child(4).setText(0, "Default flags")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.topLevelItem(3).setText(0, "Help")
        self.verticalLayout.addWidget(self.treeWidget)
        self.layout.addLayout(self.verticalLayout)
        self.currentTab = QtWidgets.QWidget(Dialog)
        self.currentTab.setObjectName("currentTab")
        self.layout.addWidget(self.currentTab)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Settings"))
        self.saveButton.setText(_translate("Dialog", "Save"))
        self.treeWidget.headerItem().setText(0, _translate("Dialog", "1"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.setSortingEnabled(__sortingEnabled)

