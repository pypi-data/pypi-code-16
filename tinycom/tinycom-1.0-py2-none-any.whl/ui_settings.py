# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tinycom/settings.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from .qt import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName(_fromUtf8("SettingsDialog"))
        SettingsDialog.resize(415, 283)
        self.verticalLayout = QtGui.QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(SettingsDialog)
        self.label_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_2.setFrameShadow(QtGui.QFrame.Plain)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.baudrate = QtGui.QComboBox(SettingsDialog)
        self.baudrate.setEditable(False)
        self.baudrate.setObjectName(_fromUtf8("baudrate"))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.baudrate.addItem(_fromUtf8(""))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.baudrate)
        self.label_4 = QtGui.QLabel(SettingsDialog)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_4)
        self.bytesize = QtGui.QComboBox(SettingsDialog)
        self.bytesize.setObjectName(_fromUtf8("bytesize"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.bytesize)
        self.label_5 = QtGui.QLabel(SettingsDialog)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_5)
        self.stopbits = QtGui.QComboBox(SettingsDialog)
        self.stopbits.setObjectName(_fromUtf8("stopbits"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.stopbits)
        self.label_6 = QtGui.QLabel(SettingsDialog)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_6)
        self.parity = QtGui.QComboBox(SettingsDialog)
        self.parity.setObjectName(_fromUtf8("parity"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.parity)
        self.label = QtGui.QLabel(SettingsDialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label)
        self.xonxoff = QtGui.QCheckBox(SettingsDialog)
        self.xonxoff.setObjectName(_fromUtf8("xonxoff"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.xonxoff)
        self.rtscts = QtGui.QCheckBox(SettingsDialog)
        self.rtscts.setObjectName(_fromUtf8("rtscts"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.rtscts)
        self.dsrdtr = QtGui.QCheckBox(SettingsDialog)
        self.dsrdtr.setObjectName(_fromUtf8("dsrdtr"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.dsrdtr)
        self.label_3 = QtGui.QLabel(SettingsDialog)
        self.label_3.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.port = QtGui.QComboBox(SettingsDialog)
        self.port.setEditable(True)
        self.port.setInsertPolicy(QtGui.QComboBox.InsertAtCurrent)
        self.port.setObjectName(_fromUtf8("port"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.port)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Open)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SettingsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SettingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Open Port", None))
        self.label_2.setText(_translate("SettingsDialog", "Baud rate:", None))
        self.baudrate.setToolTip(_translate("SettingsDialog", "Port baud rate.", None))
        self.baudrate.setItemText(0, _translate("SettingsDialog", "600", None))
        self.baudrate.setItemText(1, _translate("SettingsDialog", "1200", None))
        self.baudrate.setItemText(2, _translate("SettingsDialog", "2400", None))
        self.baudrate.setItemText(3, _translate("SettingsDialog", "4800", None))
        self.baudrate.setItemText(4, _translate("SettingsDialog", "9600", None))
        self.baudrate.setItemText(5, _translate("SettingsDialog", "14400", None))
        self.baudrate.setItemText(6, _translate("SettingsDialog", "19200", None))
        self.baudrate.setItemText(7, _translate("SettingsDialog", "38400", None))
        self.baudrate.setItemText(8, _translate("SettingsDialog", "57600", None))
        self.baudrate.setItemText(9, _translate("SettingsDialog", "115200", None))
        self.baudrate.setItemText(10, _translate("SettingsDialog", "230400", None))
        self.baudrate.setItemText(11, _translate("SettingsDialog", "460800", None))
        self.baudrate.setItemText(12, _translate("SettingsDialog", "576000", None))
        self.baudrate.setItemText(13, _translate("SettingsDialog", "921600", None))
        self.label_4.setText(_translate("SettingsDialog", "Data bits:", None))
        self.bytesize.setToolTip(_translate("SettingsDialog", "Port data bits.", None))
        self.label_5.setText(_translate("SettingsDialog", "Stop bits:", None))
        self.stopbits.setToolTip(_translate("SettingsDialog", "Port stop bits.", None))
        self.label_6.setText(_translate("SettingsDialog", "Parity:", None))
        self.parity.setToolTip(_translate("SettingsDialog", "Port parity.", None))
        self.label.setText(_translate("SettingsDialog", "Flow Control:", None))
        self.xonxoff.setToolTip(_translate("SettingsDialog", "Software flow control.", None))
        self.xonxoff.setText(_translate("SettingsDialog", "XON/XOFF", None))
        self.rtscts.setToolTip(_translate("SettingsDialog", "Hardware flow control.", None))
        self.rtscts.setText(_translate("SettingsDialog", "RTS/CTS", None))
        self.dsrdtr.setToolTip(_translate("SettingsDialog", "Hardware flow control.", None))
        self.dsrdtr.setText(_translate("SettingsDialog", "DSR/DTR", None))
        self.label_3.setText(_translate("SettingsDialog", "Device:", None))
        self.port.setToolTip(_translate("SettingsDialog", "Serial port.", None))

from . import tinycom_rc
