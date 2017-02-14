# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/add_repo.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_AddRepoDialog(object):
    def setupUi(self, AddRepoDialog):
        AddRepoDialog.setObjectName("AddRepoDialog")
        AddRepoDialog.resize(364, 111)
        AddRepoDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddRepoDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(AddRepoDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.source = QtWidgets.QLineEdit(AddRepoDialog)
        self.source.setObjectName("source")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.source)
        self.title = QtWidgets.QLineEdit(AddRepoDialog)
        self.title.setObjectName("title")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.title)
        self.label_3 = QtWidgets.QLabel(AddRepoDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(AddRepoDialog)
        self.okButton.setDefault(True)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(AddRepoDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(AddRepoDialog)
        QtCore.QMetaObject.connectSlotsByName(AddRepoDialog)

    def retranslateUi(self, AddRepoDialog):
        _translate = QtCore.QCoreApplication.translate
        AddRepoDialog.setWindowTitle(_translate("AddRepoDialog", "Add a new mod source"))
        self.label_2.setText(_translate("AddRepoDialog", "Source:"))
        self.label_3.setText(_translate("AddRepoDialog", "Title:"))
        self.okButton.setText(_translate("AddRepoDialog", "OK"))
        self.cancelButton.setText(_translate("AddRepoDialog", "Cancel"))

