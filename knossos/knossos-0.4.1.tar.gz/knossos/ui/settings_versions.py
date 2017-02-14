# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_versions.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_VersionSettingsForm(object):
    def setupUi(self, VersionSettingsForm):
        VersionSettingsForm.setObjectName("VersionSettingsForm")
        VersionSettingsForm.resize(400, 300)
        VersionSettingsForm.setWindowTitle("Form")
        self.verticalLayout = QtWidgets.QVBoxLayout(VersionSettingsForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(VersionSettingsForm)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(VersionSettingsForm)
        QtCore.QMetaObject.connectSlotsByName(VersionSettingsForm)

    def retranslateUi(self, VersionSettingsForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("VersionSettingsForm", "Nothing to see here... move along."))

