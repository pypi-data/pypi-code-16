# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_audio.ui'
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
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.playbackDevice = QtWidgets.QComboBox(Form)
        self.playbackDevice.setObjectName("playbackDevice")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.playbackDevice)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.captureDevice = QtWidgets.QComboBox(Form)
        self.captureDevice.setObjectName("captureDevice")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.captureDevice)
        self.enableEFX = QtWidgets.QCheckBox(Form)
        self.enableEFX.setObjectName("enableEFX")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.enableEFX)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.sampleRate = QtWidgets.QSpinBox(Form)
        self.sampleRate.setMaximum(1000000)
        self.sampleRate.setSingleStep(100)
        self.sampleRate.setObjectName("sampleRate")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.sampleRate)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_2.setText(_translate("Form", "Playback device: "))
        self.label.setText(_translate("Form", "Capture device: "))
        self.enableEFX.setText(_translate("Form", "Enable EFX"))
        self.label_3.setText(_translate("Form", "Sample rate:"))
        self.sampleRate.setSuffix(_translate("Form", " Hz"))

