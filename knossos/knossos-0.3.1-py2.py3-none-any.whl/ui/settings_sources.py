# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_sources.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.sourceList = QtWidgets.QListWidget(Form)
        self.sourceList.setDragEnabled(True)
        self.sourceList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.sourceList.setObjectName("sourceList")
        self.verticalLayout.addWidget(self.sourceList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addSource = QtWidgets.QPushButton(Form)
        self.addSource.setObjectName("addSource")
        self.horizontalLayout.addWidget(self.addSource)
        self.editSource = QtWidgets.QPushButton(Form)
        self.editSource.setObjectName("editSource")
        self.horizontalLayout.addWidget(self.editSource)
        self.removeSource = QtWidgets.QPushButton(Form)
        self.removeSource.setObjectName("removeSource")
        self.horizontalLayout.addWidget(self.removeSource)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.addSource.setText(_translate("Form", "Add"))
        self.editSource.setText(_translate("Form", "Edit"))
        self.removeSource.setText(_translate("Form", "Remove"))

