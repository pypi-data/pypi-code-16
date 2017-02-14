# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_input.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_InputSettingsForm(object):
    def setupUi(self, InputSettingsForm):
        InputSettingsForm.setObjectName("InputSettingsForm")
        InputSettingsForm.resize(400, 300)
        InputSettingsForm.setWindowTitle("Form")
        self.formLayout = QtWidgets.QFormLayout(InputSettingsForm)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(InputSettingsForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.keyLayout = QtWidgets.QComboBox(InputSettingsForm)
        self.keyLayout.setObjectName("keyLayout")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.keyLayout)
        self.useSetxkbmap = QtWidgets.QCheckBox(InputSettingsForm)
        self.useSetxkbmap.setObjectName("useSetxkbmap")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.useSetxkbmap)
        self.label_2 = QtWidgets.QLabel(InputSettingsForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.controller = QtWidgets.QComboBox(InputSettingsForm)
        self.controller.setObjectName("controller")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.controller)

        self.retranslateUi(InputSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(InputSettingsForm)

    def retranslateUi(self, InputSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("InputSettingsForm", "Layout: "))
        self.useSetxkbmap.setText(_translate("InputSettingsForm", "Use \"setxkbmap\""))
        self.label_2.setText(_translate("InputSettingsForm", "Controller: "))

