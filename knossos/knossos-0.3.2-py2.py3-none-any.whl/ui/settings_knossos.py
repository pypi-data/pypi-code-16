# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_knossos.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(398, 299)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.versionLabel = QtWidgets.QLabel(Form)
        self.versionLabel.setObjectName("versionLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.versionLabel)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.maxDownloads = QtWidgets.QSpinBox(Form)
        self.maxDownloads.setMaximum(5)
        self.maxDownloads.setObjectName("maxDownloads")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.maxDownloads)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.updateChannel = QtWidgets.QComboBox(Form)
        self.updateChannel.setObjectName("updateChannel")
        self.updateChannel.addItem("")
        self.updateChannel.addItem("")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.updateChannel)
        self.updateNotify = QtWidgets.QCheckBox(Form)
        self.updateNotify.setObjectName("updateNotify")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.updateNotify)
        self.debugLog = QtWidgets.QPushButton(Form)
        self.debugLog.setObjectName("debugLog")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.debugLog)
        self.clearHashes = QtWidgets.QPushButton(Form)
        self.clearHashes.setObjectName("clearHashes")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.clearHashes)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.reportErrors = QtWidgets.QCheckBox(Form)
        self.reportErrors.setObjectName("reportErrors")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.reportErrors)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Version:"))
        self.versionLabel.setText(_translate("Form", "?"))
        self.label_2.setText(_translate("Form", "Parallel downloads:"))
        self.label_3.setText(_translate("Form", "Update channel: "))
        self.updateChannel.setItemText(0, _translate("Form", "stable"))
        self.updateChannel.setItemText(1, _translate("Form", "develop"))
        self.updateNotify.setText(_translate("Form", "Display update notifications"))
        self.debugLog.setText(_translate("Form", "Open Knossos\' debug log"))
        self.clearHashes.setText(_translate("Form", "Clear the checksum cache"))
        self.label_5.setText(_translate("Form", "Troubleshooting:"))
        self.reportErrors.setText(_translate("Form", "Automatically report errors"))

