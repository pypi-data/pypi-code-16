# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_fso.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.build = QtWidgets.QComboBox(Form)
        self.build.setObjectName("build")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.build)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.fs2PathLabel = QtWidgets.QLabel(Form)
        self.fs2PathLabel.setObjectName("fs2PathLabel")
        self.horizontalLayout.addWidget(self.fs2PathLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.browseButton = QtWidgets.QPushButton(Form)
        self.browseButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.browseButton.setObjectName("browseButton")
        self.horizontalLayout.addWidget(self.browseButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.openLog = QtWidgets.QPushButton(Form)
        self.openLog.setObjectName("openLog")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.openLog)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "FS2 Path: "))
        self.label_2.setText(_translate("Form", "FSO Build: "))
        self.fs2PathLabel.setText(_translate("Form", "..."))
        self.browseButton.setText(_translate("Form", "Browse"))
        self.openLog.setText(_translate("Form", "Open fs2_open.log"))

