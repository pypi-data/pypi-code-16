# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings2.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(575, 400)
        SettingsDialog.setModal(True)
        self.layout = QtWidgets.QHBoxLayout(SettingsDialog)
        self.layout.setObjectName("layout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.saveButton = QtWidgets.QPushButton(SettingsDialog)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout.addWidget(self.saveButton)
        self.treeWidget = QtWidgets.QTreeWidget(SettingsDialog)
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
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_0.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.verticalLayout.addWidget(self.treeWidget)
        self.layout.addLayout(self.verticalLayout)
        self.currentTab = QtWidgets.QWidget(SettingsDialog)
        self.currentTab.setObjectName("currentTab")
        self.layout.addWidget(self.currentTab)

        self.retranslateUi(SettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Settings"))
        self.saveButton.setText(_translate("SettingsDialog", "Save"))
        self.treeWidget.headerItem().setText(0, _translate("SettingsDialog", "1"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("SettingsDialog", "About Knossos"))
        self.treeWidget.topLevelItem(1).setText(0, _translate("SettingsDialog", "Launcher settings"))
        self.treeWidget.topLevelItem(1).child(0).setText(0, _translate("SettingsDialog", "Retail install"))
        self.treeWidget.topLevelItem(1).child(1).setText(0, _translate("SettingsDialog", "Mod sources"))
        self.treeWidget.topLevelItem(1).child(2).setText(0, _translate("SettingsDialog", "Library paths"))
        self.treeWidget.topLevelItem(2).setText(0, _translate("SettingsDialog", "Game settings"))
        self.treeWidget.topLevelItem(2).child(0).setText(0, _translate("SettingsDialog", "Video"))
        self.treeWidget.topLevelItem(2).child(1).setText(0, _translate("SettingsDialog", "Audio"))
        self.treeWidget.topLevelItem(2).child(2).setText(0, _translate("SettingsDialog", "Input"))
        self.treeWidget.topLevelItem(2).child(3).setText(0, _translate("SettingsDialog", "Network"))
        self.treeWidget.topLevelItem(2).child(4).setText(0, _translate("SettingsDialog", "Default flags"))
        self.treeWidget.topLevelItem(3).setText(0, _translate("SettingsDialog", "Help"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)

