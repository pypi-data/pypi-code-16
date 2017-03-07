"""QColorSetWidget"""
# coding:utf-8
from __future__ import division, print_function, unicode_literals, absolute_import
# noinspection PyUnresolvedReferences
from future_builtins import *

from PySide.QtGui import *
from PySide.QtCore import *

class QColorSetWidget(QWidget):
    colorChanged = Signal(str)

    def __init__(self, parent=None):
        super(QColorSetWidget, self).__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.color = QColor("white")
        self.set_color_mode(False)

        self.ui.spinBox_Hue.setValue(self.color.hue())
        self.ui.spinBox_Saturation.setValue(self.color.saturation())
        self.ui.spinBox_Value.setValue(self.color.value())

        self.ui.spinBox_Blue.setValue(self.color.blue())
        self.ui.spinBox_Green.setValue(self.color.green())
        self.ui.spinBox_Red.setValue(self.color.red())

        self.ui.spinBox_Alpha.setValue(self.color.alpha())

    @Slot()
    def on_radioButton_HSV_clicked(self):
        if self.ui.radioButton_HSV.isChecked():
            self.set_color_mode(False)

    @Slot()
    def on_radioButton_RGB_clicked(self):
        if self.ui.radioButton_RGB.isChecked():
            self.set_color_mode(True)

    def set_color_mode(self, color_mode):
        self.color_mode = color_mode

        self.ui.radioButton_RGB.setChecked(color_mode)
        self.ui.spinBox_Blue.setEnabled(color_mode)
        self.ui.spinBox_Green.setEnabled(color_mode)
        self.ui.spinBox_Red.setEnabled(color_mode)

        self.ui.radioButton_HSV.setChecked(not color_mode)
        self.ui.spinBox_Hue.setEnabled(not color_mode)
        self.ui.spinBox_Saturation.setEnabled(not color_mode)
        self.ui.spinBox_Value.setEnabled(not color_mode)

    @Slot()
    def on_spinBox_Hue_valueChanged(self):
        if self.ui.spinBox_Hue.hasFocus():
            self.spinboxToColor()

    @Slot()
    def on_spinBox_Saturation_valueChanged(self):
        if self.ui.spinBox_Saturation.hasFocus():
            self.spinboxToColor()

    @Slot()
    def on_spinBox_Value_valueChanged(self):
        if self.ui.spinBox_Value.hasFocus():
            self.spinboxToColor()

    @Slot()
    def on_spinBox_Red_valueChanged(self):
        if self.ui.spinBox_Red.hasFocus():
            self.spinboxToColor()

    @Slot()
    def on_spinBox_Blue_valueChanged(self):
        if self.ui.spinBox_Blue.hasFocus():
            self.spinboxToColor()

    @Slot()
    def on_spinBox_Green_valueChanged(self):
        if self.ui.spinBox_Green.hasFocus():
            self.spinboxToColor()

    @Slot()
    def on_spinBox_Alpha_valueChanged(self):
        if self.ui.spinBox_Alpha.hasFocus():
            self.color.setAlpha(self.ui.spinBox_Alpha.value())
            self.colorChanged.emit('colorChanged')

    def spinboxToColor(self):
        if self.color_mode:
            self.color = QColor(
                self.ui.spinBox_Red.value(),
                self.ui.spinBox_Green.value(),
                self.ui.spinBox_Blue.value(),
                self.ui.spinBox_Alpha.value()
            )
            self.colorToSpinbox_hsv()
        else:
            self.color.setHsv(
                self.ui.spinBox_Hue.value(),
                self.ui.spinBox_Saturation.value(),
                self.ui.spinBox_Value.value(),
                self.ui.spinBox_Alpha.value()
             )
            self.colorToSpinbox_rgb()
        self.colorChanged.emit('colorChanged')

    def colorToSpinbox_rgb(self):
        self.ui.spinBox_Blue.setValue(self.color.blue())
        self.ui.spinBox_Green.setValue(self.color.green())
        self.ui.spinBox_Red.setValue(self.color.red())

    def colorToSpinbox_hsv(self):
        self.ui.spinBox_Hue.setValue(self.color.hue())
        self.ui.spinBox_Saturation.setValue(self.color.saturation())
        self.ui.spinBox_Value.setValue(self.color.value())

    def getColor(self):
        return(self.color)

    def setColor(self, color):
        self.color = QColor(color)
        self.colorToSpinbox_rgb()
        self.colorToSpinbox_hsv()
        self.ui.spinBox_Alpha.setValue(self.color.alpha())

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        # Dialog.resize(332, 82)
        self.layoutWidget = QWidget(Dialog)
        # self.layoutWidget.setGeometry(QRect(10, 10, 321, 74))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.radioButton_HSV = QRadioButton(self.layoutWidget)
        self.radioButton_HSV.setObjectName("radioButton_HSV")
        self.gridLayout.addWidget(self.radioButton_HSV, 0, 0, 1, 1)
        self.spinBox_Hue = QSpinBox(self.layoutWidget)
        self.spinBox_Hue.setMaximum(360)
        self.spinBox_Hue.setObjectName("spinBox_Hue")
        self.gridLayout.addWidget(self.spinBox_Hue, 0, 1, 1, 1)
        self.spinBox_Saturation = QSpinBox(self.layoutWidget)
        self.spinBox_Saturation.setMaximum(255)
        self.spinBox_Saturation.setObjectName("spinBox_Saturation")
        self.gridLayout.addWidget(self.spinBox_Saturation, 0, 2, 1, 1)
        self.spinBox_Value = QSpinBox(self.layoutWidget)
        self.spinBox_Value.setMaximum(255)
        self.spinBox_Value.setObjectName("spinBox_Value")
        self.gridLayout.addWidget(self.spinBox_Value, 0, 3, 1, 1)
        self.radioButton_RGB = QRadioButton(self.layoutWidget)
        self.radioButton_RGB.setLayoutDirection(Qt.LeftToRight)
        self.radioButton_RGB.setObjectName("radioButton_RGB")
        self.gridLayout.addWidget(self.radioButton_RGB, 1, 0, 1, 1)
        self.spinBox_Green = QSpinBox(self.layoutWidget)
        self.spinBox_Green.setMaximum(255)
        self.spinBox_Green.setObjectName("spinBox_Green")
        self.gridLayout.addWidget(self.spinBox_Green, 1, 2, 1, 1)
        self.spinBox_Blue = QSpinBox(self.layoutWidget)
        self.spinBox_Blue.setMaximum(255)
        self.spinBox_Blue.setObjectName("spinBox_Blue")
        self.gridLayout.addWidget(self.spinBox_Blue, 1, 3, 1, 1)
        self.label = QLabel(self.layoutWidget)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.spinBox_Alpha = QSpinBox(self.layoutWidget)
        self.spinBox_Alpha.setMaximum(255)
        self.spinBox_Alpha.setObjectName("spinBox_Alpha")
        self.gridLayout.addWidget(self.spinBox_Alpha, 2, 1, 1, 1)
        self.spinBox_Red = QSpinBox(self.layoutWidget)
        self.spinBox_Red.setMaximum(255)
        self.spinBox_Red.setObjectName("spinBox_Red")
        self.gridLayout.addWidget(self.spinBox_Red, 1, 1, 1, 1)

        self.radioButton_HSV.setText("HSV")
        self.radioButton_RGB.setText("RGB")
        self.label.setText("Alpha")

        QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.radioButton_HSV, self.spinBox_Hue)
        Dialog.setTabOrder(self.spinBox_Hue, self.spinBox_Saturation)
        Dialog.setTabOrder(self.spinBox_Saturation, self.spinBox_Value)
        Dialog.setTabOrder(self.spinBox_Value, self.radioButton_RGB)
        Dialog.setTabOrder(self.radioButton_RGB, self.spinBox_Red)
        Dialog.setTabOrder(self.spinBox_Red, self.spinBox_Green)
        Dialog.setTabOrder(self.spinBox_Green, self.spinBox_Blue)
        Dialog.setTabOrder(self.spinBox_Blue, self.spinBox_Alpha)

        Dialog.resize(200, 70)
