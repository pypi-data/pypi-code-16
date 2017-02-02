# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/log_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(648, 661)
        Dialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pathLabel = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.pathLabel.setFont(font)
        self.pathLabel.setObjectName("pathLabel")
        self.verticalLayout.addWidget(self.pathLabel)
        self.content = QtWidgets.QTextBrowser(Dialog)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.content)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "fs2_open.log"))
        self.pathLabel.setText(_translate("Dialog", "fs2_open.log"))

