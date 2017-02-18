# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_video.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_VideoSettingsForm(object):
    def setupUi(self, VideoSettingsForm):
        VideoSettingsForm.setObjectName("VideoSettingsForm")
        VideoSettingsForm.resize(400, 300)
        VideoSettingsForm.setWindowTitle("Form")
        self.formLayout = QtWidgets.QFormLayout(VideoSettingsForm)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(VideoSettingsForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.resolution = QtWidgets.QComboBox(VideoSettingsForm)
        self.resolution.setObjectName("resolution")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.resolution)
        self.label_2 = QtWidgets.QLabel(VideoSettingsForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.colorDepth = QtWidgets.QComboBox(VideoSettingsForm)
        self.colorDepth.setObjectName("colorDepth")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.colorDepth)
        self.label_3 = QtWidgets.QLabel(VideoSettingsForm)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(VideoSettingsForm)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtWidgets.QLabel(VideoSettingsForm)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.textureFilter = QtWidgets.QComboBox(VideoSettingsForm)
        self.textureFilter.setObjectName("textureFilter")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.textureFilter)
        self.antialiasing = QtWidgets.QComboBox(VideoSettingsForm)
        self.antialiasing.setObjectName("antialiasing")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.antialiasing)
        self.anisotropic = QtWidgets.QComboBox(VideoSettingsForm)
        self.anisotropic.setObjectName("anisotropic")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.anisotropic)

        self.retranslateUi(VideoSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(VideoSettingsForm)

    def retranslateUi(self, VideoSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("VideoSettingsForm", "Resolution: "))
        self.label_2.setText(_translate("VideoSettingsForm", "Color depth: "))
        self.label_3.setText(_translate("VideoSettingsForm", "Texture filter: "))
        self.label_4.setText(_translate("VideoSettingsForm", "Antialiasing: "))
        self.label_5.setText(_translate("VideoSettingsForm", "Anisotropic filtering: "))

