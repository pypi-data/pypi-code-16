# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_knossos.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_KnossosSettingsForm(object):
    def setupUi(self, KnossosSettingsForm):
        KnossosSettingsForm.setObjectName("KnossosSettingsForm")
        KnossosSettingsForm.resize(398, 299)
        KnossosSettingsForm.setWindowTitle("Form")
        self.formLayout = QtWidgets.QFormLayout(KnossosSettingsForm)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(KnossosSettingsForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.versionLabel = QtWidgets.QLabel(KnossosSettingsForm)
        self.versionLabel.setObjectName("versionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.versionLabel)
        self.label_2 = QtWidgets.QLabel(KnossosSettingsForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.maxDownloads = QtWidgets.QSpinBox(KnossosSettingsForm)
        self.maxDownloads.setMaximum(5)
        self.maxDownloads.setObjectName("maxDownloads")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.maxDownloads)
        self.label_3 = QtWidgets.QLabel(KnossosSettingsForm)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.updateChannel = QtWidgets.QComboBox(KnossosSettingsForm)
        self.updateChannel.setObjectName("updateChannel")
        self.updateChannel.addItem("")
        self.updateChannel.addItem("")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.updateChannel)
        self.updateNotify = QtWidgets.QCheckBox(KnossosSettingsForm)
        self.updateNotify.setObjectName("updateNotify")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.updateNotify)
        self.debugLog = QtWidgets.QPushButton(KnossosSettingsForm)
        self.debugLog.setObjectName("debugLog")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.debugLog)
        self.clearHashes = QtWidgets.QPushButton(KnossosSettingsForm)
        self.clearHashes.setObjectName("clearHashes")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.clearHashes)
        self.label_5 = QtWidgets.QLabel(KnossosSettingsForm)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.reportErrors = QtWidgets.QCheckBox(KnossosSettingsForm)
        self.reportErrors.setObjectName("reportErrors")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.reportErrors)
        self.label_4 = QtWidgets.QLabel(KnossosSettingsForm)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.langSelect = QtWidgets.QComboBox(KnossosSettingsForm)
        self.langSelect.setObjectName("langSelect")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.langSelect)

        self.retranslateUi(KnossosSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(KnossosSettingsForm)

    def retranslateUi(self, KnossosSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("KnossosSettingsForm", "Version:"))
        self.versionLabel.setText(_translate("KnossosSettingsForm", "?"))
        self.label_2.setText(_translate("KnossosSettingsForm", "Parallel downloads:"))
        self.label_3.setText(_translate("KnossosSettingsForm", "Update channel: "))
        self.updateChannel.setItemText(0, _translate("KnossosSettingsForm", "stable"))
        self.updateChannel.setItemText(1, _translate("KnossosSettingsForm", "develop"))
        self.updateNotify.setText(_translate("KnossosSettingsForm", "Display update notifications"))
        self.debugLog.setText(_translate("KnossosSettingsForm", "Open Knossos\' debug log"))
        self.clearHashes.setText(_translate("KnossosSettingsForm", "Clear the checksum cache"))
        self.label_5.setText(_translate("KnossosSettingsForm", "Troubleshooting:"))
        self.reportErrors.setText(_translate("KnossosSettingsForm", "Automatically report errors"))
        self.label_4.setText(_translate("KnossosSettingsForm", "Language:"))

