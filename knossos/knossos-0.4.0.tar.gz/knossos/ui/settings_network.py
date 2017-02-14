# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_network.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_NetworkSettingsForm(object):
    def setupUi(self, NetworkSettingsForm):
        NetworkSettingsForm.setObjectName("NetworkSettingsForm")
        NetworkSettingsForm.resize(400, 300)
        NetworkSettingsForm.setWindowTitle("Form")
        self.formLayout = QtWidgets.QFormLayout(NetworkSettingsForm)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(NetworkSettingsForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(NetworkSettingsForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(NetworkSettingsForm)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(NetworkSettingsForm)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.connectionType = QtWidgets.QComboBox(NetworkSettingsForm)
        self.connectionType.setObjectName("connectionType")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.connectionType)
        self.connectionSpeed = QtWidgets.QComboBox(NetworkSettingsForm)
        self.connectionSpeed.setObjectName("connectionSpeed")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.connectionSpeed)
        self.localPort = QtWidgets.QLineEdit(NetworkSettingsForm)
        self.localPort.setObjectName("localPort")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.localPort)
        self.forceAddress = QtWidgets.QLineEdit(NetworkSettingsForm)
        self.forceAddress.setObjectName("forceAddress")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.forceAddress)

        self.retranslateUi(NetworkSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(NetworkSettingsForm)

    def retranslateUi(self, NetworkSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("NetworkSettingsForm", "Connection type: "))
        self.label_2.setText(_translate("NetworkSettingsForm", "Connection speed: "))
        self.label_3.setText(_translate("NetworkSettingsForm", "Force local port: "))
        self.label_4.setText(_translate("NetworkSettingsForm", "Force IP address: "))

