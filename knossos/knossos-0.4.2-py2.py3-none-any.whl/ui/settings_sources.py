# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings_sources.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_ModSourcesForm(object):
    def setupUi(self, ModSourcesForm):
        ModSourcesForm.setObjectName("ModSourcesForm")
        ModSourcesForm.resize(400, 300)
        ModSourcesForm.setWindowTitle("Form")
        self.verticalLayout = QtWidgets.QVBoxLayout(ModSourcesForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.sourceList = QtWidgets.QListWidget(ModSourcesForm)
        self.sourceList.setDragEnabled(True)
        self.sourceList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.sourceList.setObjectName("sourceList")
        self.verticalLayout.addWidget(self.sourceList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addSource = QtWidgets.QPushButton(ModSourcesForm)
        self.addSource.setObjectName("addSource")
        self.horizontalLayout.addWidget(self.addSource)
        self.editSource = QtWidgets.QPushButton(ModSourcesForm)
        self.editSource.setObjectName("editSource")
        self.horizontalLayout.addWidget(self.editSource)
        self.removeSource = QtWidgets.QPushButton(ModSourcesForm)
        self.removeSource.setObjectName("removeSource")
        self.horizontalLayout.addWidget(self.removeSource)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ModSourcesForm)
        QtCore.QMetaObject.connectSlotsByName(ModSourcesForm)

    def retranslateUi(self, ModSourcesForm):
        _translate = QtCore.QCoreApplication.translate
        self.addSource.setText(_translate("ModSourcesForm", "Add"))
        self.editSource.setText(_translate("ModSourcesForm", "Edit"))
        self.removeSource.setText(_translate("ModSourcesForm", "Remove"))

