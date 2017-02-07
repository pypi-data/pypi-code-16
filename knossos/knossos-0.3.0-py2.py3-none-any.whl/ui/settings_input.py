# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_input.ui'
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
        self.keyLayout = QtWidgets.QComboBox(Form)
        self.keyLayout.setObjectName("keyLayout")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.keyLayout)
        self.useSetxkbmap = QtWidgets.QCheckBox(Form)
        self.useSetxkbmap.setObjectName("useSetxkbmap")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.useSetxkbmap)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.controller = QtWidgets.QComboBox(Form)
        self.controller.setObjectName("controller")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.controller)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Layout: "))
        self.useSetxkbmap.setText(_translate("Form", "Use \"setxkbmap\""))
        self.label_2.setText(_translate("Form", "Controller: "))

