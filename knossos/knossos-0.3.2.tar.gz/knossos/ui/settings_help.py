# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_help.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p>If you need help, you can either check <a href=\"http://www.hard-light.net/forums/index.php?topic=86364.msg1768735#msg1768735\"><span style=\" text-decoration: underline; color:#0000ff;\">this release post</span></a> or <a href=\"https://github.com/ngld/knossos/issues\"><span style=\" text-decoration: underline; color:#0000ff;\">check the reported issues</span></a>.</p></body></html>"))

