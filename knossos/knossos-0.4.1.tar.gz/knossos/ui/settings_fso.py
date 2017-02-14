# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_fso.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_FsoSettingsForm(object):
    def setupUi(self, FsoSettingsForm):
        FsoSettingsForm.setObjectName("FsoSettingsForm")
        FsoSettingsForm.resize(400, 300)
        FsoSettingsForm.setWindowTitle("Form")
        self.formLayout = QtWidgets.QFormLayout(FsoSettingsForm)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(FsoSettingsForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(FsoSettingsForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.build = QtWidgets.QComboBox(FsoSettingsForm)
        self.build.setObjectName("build")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.build)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.fs2PathLabel = QtWidgets.QLabel(FsoSettingsForm)
        self.fs2PathLabel.setObjectName("fs2PathLabel")
        self.horizontalLayout.addWidget(self.fs2PathLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.browseButton = QtWidgets.QPushButton(FsoSettingsForm)
        self.browseButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.browseButton.setObjectName("browseButton")
        self.horizontalLayout.addWidget(self.browseButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_3 = QtWidgets.QLabel(FsoSettingsForm)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.openLog = QtWidgets.QPushButton(FsoSettingsForm)
        self.openLog.setObjectName("openLog")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.openLog)
        self.fredBuild = QtWidgets.QComboBox(FsoSettingsForm)
        self.fredBuild.setObjectName("fredBuild")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.fredBuild)

        self.retranslateUi(FsoSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(FsoSettingsForm)

    def retranslateUi(self, FsoSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("FsoSettingsForm", "FS2 Path: "))
        self.label_2.setText(_translate("FsoSettingsForm", "FSO Build: "))
        self.fs2PathLabel.setText(_translate("FsoSettingsForm", "..."))
        self.browseButton.setText(_translate("FsoSettingsForm", "Browse"))
        self.label_3.setText(_translate("FsoSettingsForm", "FRED2 Build:"))
        self.openLog.setText(_translate("FsoSettingsForm", "Open fs2_open.log"))

