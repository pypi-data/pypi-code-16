# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_libs.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_LibPathForm(object):
    def setupUi(self, LibPathForm):
        LibPathForm.setObjectName("LibPathForm")
        LibPathForm.resize(404, 300)
        LibPathForm.setWindowTitle("Form")
        self.gridLayout = QtWidgets.QGridLayout(LibPathForm)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(LibPathForm)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.openAlBtn = QtWidgets.QPushButton(LibPathForm)
        self.openAlBtn.setObjectName("openAlBtn")
        self.gridLayout.addWidget(self.openAlBtn, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.testBtn = QtWidgets.QPushButton(LibPathForm)
        self.testBtn.setObjectName("testBtn")
        self.gridLayout.addWidget(self.testBtn, 4, 2, 1, 1)
        self.sdlPath = QtWidgets.QLineEdit(LibPathForm)
        self.sdlPath.setObjectName("sdlPath")
        self.gridLayout.addWidget(self.sdlPath, 1, 1, 1, 1)
        self.openAlPath = QtWidgets.QLineEdit(LibPathForm)
        self.openAlPath.setObjectName("openAlPath")
        self.gridLayout.addWidget(self.openAlPath, 3, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(LibPathForm)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.sdlBtn = QtWidgets.QPushButton(LibPathForm)
        self.sdlBtn.setObjectName("sdlBtn")
        self.gridLayout.addWidget(self.sdlBtn, 1, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(LibPathForm)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 3)
        self.label_4 = QtWidgets.QLabel(LibPathForm)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 5, 1, 1, 1)

        self.retranslateUi(LibPathForm)
        QtCore.QMetaObject.connectSlotsByName(LibPathForm)

    def retranslateUi(self, LibPathForm):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("LibPathForm", "SDL2:"))
        self.openAlBtn.setText(_translate("LibPathForm", "Browse"))
        self.testBtn.setText(_translate("LibPathForm", "Test"))
        self.label_2.setText(_translate("LibPathForm", "OpenAL:"))
        self.sdlBtn.setText(_translate("LibPathForm", "Browse"))
        self.label_3.setText(_translate("LibPathForm", "Here you can specifiy the paths to your SDL2 and OpenAL libraries. Normally you won\'t have to change this.\n"
"If a text field contains \"auto\", it means that Knossos will try to find the libraries automatically.\n"
""))
        self.label_4.setText(_translate("LibPathForm", "If you change a path, please click on \"Test\" to verify that Knossos can use the libraries you specified before saving."))

