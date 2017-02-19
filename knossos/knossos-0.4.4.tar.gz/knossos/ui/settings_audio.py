# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_audio.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_AudioSettingsForm(object):
    def setupUi(self, AudioSettingsForm):
        AudioSettingsForm.setObjectName("AudioSettingsForm")
        AudioSettingsForm.resize(400, 300)
        AudioSettingsForm.setWindowTitle("Form")
        self.formLayout = QtWidgets.QFormLayout(AudioSettingsForm)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(AudioSettingsForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.playbackDevice = QtWidgets.QComboBox(AudioSettingsForm)
        self.playbackDevice.setObjectName("playbackDevice")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.playbackDevice)
        self.label = QtWidgets.QLabel(AudioSettingsForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.captureDevice = QtWidgets.QComboBox(AudioSettingsForm)
        self.captureDevice.setObjectName("captureDevice")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.captureDevice)
        self.enableEFX = QtWidgets.QCheckBox(AudioSettingsForm)
        self.enableEFX.setObjectName("enableEFX")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.enableEFX)
        self.label_3 = QtWidgets.QLabel(AudioSettingsForm)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.sampleRate = QtWidgets.QSpinBox(AudioSettingsForm)
        self.sampleRate.setMaximum(1000000)
        self.sampleRate.setSingleStep(100)
        self.sampleRate.setObjectName("sampleRate")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.sampleRate)

        self.retranslateUi(AudioSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(AudioSettingsForm)

    def retranslateUi(self, AudioSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("AudioSettingsForm", "Playback device: "))
        self.label.setText(_translate("AudioSettingsForm", "Capture device: "))
        self.enableEFX.setText(_translate("AudioSettingsForm", "Enable EFX"))
        self.label_3.setText(_translate("AudioSettingsForm", "Sample rate:"))
        self.sampleRate.setSuffix(_translate("AudioSettingsForm", " Hz"))

