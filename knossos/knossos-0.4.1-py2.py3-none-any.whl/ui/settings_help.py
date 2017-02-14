# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_help.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_HelpForm(object):
    def setupUi(self, HelpForm):
        HelpForm.setObjectName("HelpForm")
        HelpForm.resize(400, 300)
        HelpForm.setWindowTitle("Form")
        self.verticalLayout = QtWidgets.QVBoxLayout(HelpForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(HelpForm)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(HelpForm)
        QtCore.QMetaObject.connectSlotsByName(HelpForm)

    def retranslateUi(self, HelpForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("HelpForm", "<html><head/><body><p>If you need help, you can either check <a href=\"http://www.hard-light.net/forums/index.php?topic=93144.0\"><span style=\" text-decoration: underline; color:#0000ff;\">this release post</span></a> or <a href=\"https://github.com/ngld/knossos/issues\"><span style=\" text-decoration: underline; color:#0000ff;\">check the reported issues</span></a>.</p></body></html>"))

