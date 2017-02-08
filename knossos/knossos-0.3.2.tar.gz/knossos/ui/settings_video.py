# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_video.ui'
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
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.resolution = QtWidgets.QComboBox(Form)
        self.resolution.setObjectName("resolution")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.resolution)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.colorDepth = QtWidgets.QComboBox(Form)
        self.colorDepth.setObjectName("colorDepth")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.colorDepth)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.textureFilter = QtWidgets.QComboBox(Form)
        self.textureFilter.setObjectName("textureFilter")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.textureFilter)
        self.antialiasing = QtWidgets.QComboBox(Form)
        self.antialiasing.setObjectName("antialiasing")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.antialiasing)
        self.anisotropic = QtWidgets.QComboBox(Form)
        self.anisotropic.setObjectName("anisotropic")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.anisotropic)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Resolution: "))
        self.label_2.setText(_translate("Form", "Color depth: "))
        self.label_3.setText(_translate("Form", "Texture filter: "))
        self.label_4.setText(_translate("Form", "Antialiasing: "))
        self.label_5.setText(_translate("Form", "Anisotropic filtering: "))

