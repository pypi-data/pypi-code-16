# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/flags.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(455, 507)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.cmdLine = QtWidgets.QPlainTextEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.cmdLine.sizePolicy().hasHeightForWidth())
        self.cmdLine.setSizePolicy(sizePolicy)
        self.cmdLine.setReadOnly(True)
        self.cmdLine.setObjectName("cmdLine")
        self.verticalLayout.addWidget(self.cmdLine)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.customFlags = QtWidgets.QLineEdit(Dialog)
        self.customFlags.setObjectName("customFlags")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.customFlags)
        self.easySetup = QtWidgets.QComboBox(Dialog)
        self.easySetup.setObjectName("easySetup")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.easySetup)
        self.listType = QtWidgets.QComboBox(Dialog)
        self.listType.setObjectName("listType")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.listType)
        self.verticalLayout.addLayout(self.formLayout)
        self.flagList = QtWidgets.QListWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.flagList.sizePolicy().hasHeightForWidth())
        self.flagList.setSizePolicy(sizePolicy)
        self.flagList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.flagList.setProperty("showDropIndicator", False)
        self.flagList.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.flagList.setObjectName("flagList")
        self.verticalLayout.addWidget(self.flagList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(Dialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.saveButton = QtWidgets.QPushButton(Dialog)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.defaultsButton = QtWidgets.QPushButton(Dialog)
        self.defaultsButton.setObjectName("defaultsButton")
        self.horizontalLayout.addWidget(self.defaultsButton)
        self.cancelButton = QtWidgets.QPushButton(Dialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Mod Flags"))
        self.label.setText(_translate("Dialog", "The complete commandline:"))
        self.label_2.setText(_translate("Dialog", "Easy Setup"))
        self.label_3.setText(_translate("Dialog", "Custom Flags"))
        self.label_4.setText(_translate("Dialog", "List Type"))
        self.okButton.setText(_translate("Dialog", "OK"))
        self.saveButton.setText(_translate("Dialog", "Save"))
        self.defaultsButton.setText(_translate("Dialog", "Use Defaults"))
        self.cancelButton.setText(_translate("Dialog", "Cancel"))

