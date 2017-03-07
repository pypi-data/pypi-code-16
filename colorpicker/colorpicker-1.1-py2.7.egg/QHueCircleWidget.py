"""QHueCircleWidget"""
# coding:utf-8
from __future__ import division, print_function, unicode_literals, absolute_import
# noinspection PyUnresolvedReferences
from future_builtins import *

from PySide.QtGui import *
from PySide.QtCore import *

import math

class QHueCircleWidget(QGraphicsView):
    PRESS_NONE = 0
    PRESS_BOX = 1
    PRESS_CIRCLE = 2

    colorChanged = Signal(str)

    def __init__(self, parent):
        super(QHueCircleWidget, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.rectF = None
        self.press_mode = self.PRESS_NONE
        self.color = QColor()
        self.color.setHsv(0, 255, 255, 255)
        self.setColor(self.color)
        self.bg_brush = QBrush(self.create_bg_pixmap())

        self.setFixedSize(200,200)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumSize(200, 200)


    def drawBackground(self, painter, rect):
        """
        :type rect: QRectF
        :type painter: QPainter
        """
        painter.save()

        painter.translate(rect.center())
        painter.setRenderHint(QPainter.Antialiasing, True)
        self.rectF = rect
        self.rectToParam()
        painter.setPen(QPen(Qt.black, 1))
        # draw select color
        painter.setBrush(self.bg_brush)
        painter.drawEllipse(-self.half_width, -self.half_height, self.width / 8, self.height / 8)
        painter.setBrush(self.color)
        painter.drawEllipse(-self.half_width, -self.half_height, self.width / 8, self.height / 8)
        # hue color circle
        painter.setBrush(self.bg_brush)
        painter.drawEllipse(0 - self.half_width, 0 - self.half_height, self.width, self.height)
        color = QColor()
        gradient = QConicalGradient(0, 0, 0)
        for _ in range(11):
            color.setHsv((10 - _) * 36, 255, 255, self.color.alpha())
            gradient.setColorAt(0.1 * _, color)
        painter.setBrush(gradient)
        painter.drawEllipse(0 - self.half_width, 0 - self.half_height, self.width, self.height)
        # center delete circle
        mini_circle_width = self.width * 3 / 4
        mini_circle_height = self.height * 3 / 4
        painter.setBrush(QPalette().brush(QPalette.Midlight))
        painter.drawEllipse(0 - mini_circle_width / 2, 0 - mini_circle_height / 2 , mini_circle_width, mini_circle_height)
        # center box saturation
        gradient = QLinearGradient(-self.quarter_width, 0, self.quarter_width, 0)
        color.setHsv(self.color.hue(), 0, 255, 255)
        gradient.setColorAt(0.0, color)
        color.setHsv(self.color.hue(), 255, 255, 255)
        gradient.setColorAt(1.0, color)
        painter.setBrush(gradient)
        painter.drawRect(-self.quarter_width, -self.quarter_height, self.half_width, self.half_height)

        painter.restore()

    def drawForeground(self, painter, rect):
        """
        :type rect: QRectF
        :type painter: QPainter
        """
        painter.save()

        painter.translate(rect.center())
        painter.setRenderHint(QPainter.Antialiasing, True)
        # center box value
        gradient = QLinearGradient(0, -self.quarter_height, 0, self.quarter_height)
        color = QColor()
        color.setHsv(0, 0, 0, 0)
        gradient.setColorAt(0.0, color)
        color.setHsv(0, 0, 0, 255)
        gradient.setColorAt(1.0, color)
        painter.setBrush(gradient)
        painter.drawRect(-self.quarter_width, -self.quarter_height, self.half_width, self.half_height)
        # lupe for Saturation / Value
        painter.setPen(QPen(QColor(255, 255, 255, 255), 1))
        painter.drawEllipse(self.sv_x - 3, self.sv_y - 3, 7, 7)
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1))
        painter.drawEllipse(self.sv_x - 2, self.sv_y - 2, 5, 5)
        # lupe for Hue
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1))
        painter.setBrush(QColor(255, 255, 255, 0))
        painter.rotate(self.color.hue())
        painter.drawRect(self.width * 3 / 8, -4, self.width / 8, 8)

        painter.restore()

    def mouseMoveEvent(self, event):
        self.clickToColor(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rectToParam()
            if self.hitBox(event.x(), event.y()):
                self.press_mode = self.PRESS_BOX
                self.clickToColor(event)
            elif self.hitCircle(event.x(), event.y()):
                self.press_mode = self.PRESS_CIRCLE
                self.clickToColor(event)
            else:
                self.press_mode = self.PRESS_NONE

    def clickToColor(self, event):
        if self.press_mode == self.PRESS_BOX:
            self.clickToBox(event)
        elif self.press_mode == self.PRESS_CIRCLE:
            self.clickCircle(event)

        self.colorChanged.emit('colorChanged')
        self.scene.update()

    def hitBox(self, x, y):
        rect = QRect(self.quarter_width, self.quarter_height, self.width * 2 / 4, self.height * 2 / 4)
        return rect.contains(x, y)

    def hitCircle(self, x, y):
        path = QPainterPath()
        path.addEllipse(0, 0, self.width, self.height)

        path2 = QPainterPath()
        path2.addEllipse(self.quarter_width / 2., self.quarter_height / 2., self.width / 4. * 3., self.height / 4. * 3.)

        pos = QPointF(x, y)
        return path.contains(pos) and not path2.contains(pos)

    def clickToBox(self, event):
        if not self.hitBox(event.x(), event.y()):
            return

        x = event.x()
        y = event.y()

        col_sat = 255 * (x - self.quarter_width) / self.half_width
        col_sat = 0 if col_sat < 0 else col_sat
        col_sat = 255 if col_sat > 255 else col_sat

        col_val = 255 * (self.half_height - (y - self.quarter_height)) / self.half_height
        col_val = 0 if col_val < 0 else col_val
        col_val = 255 if col_val > 255 else col_val

        self.color.setHsv(
            self.color.hue(),
            col_sat,
            col_val,
            self.color.alpha()
        )
        self.sv_x = x - self.half_width
        self.sv_y = y - self.half_height

    def clickCircle(self, event):
        x = event.x()
        y = event.y()

        k = int(math.degrees(math.atan2(x - self.half_width, self.half_height - y)))
        self.color.setHsv(
            (k - 90) % 360,
            self.color.saturation(),
            self.color.value(),
            self.color.alpha()
        )
        self.hue_x = x - self.half_width
        self.hue_y = y - self.half_height

    def getColor(self):
        return(self.color)

    def setColor(self, color):
        self.color = QColor(color)
        if self.rectF == None:
            self.sv_x = 0
            self.sv_y = 0
            self.hue_x = 0
            self.hue_y = 0
            self.scene.update()
        else:
            self.rectToParam()
            # SV
            self.sv_x = color.saturation() * self.half_width / 255 - self.quarter_width
            self.sv_y = (255 - color.value()) * self.half_height / 255 - self.quarter_height
            # Hue
            radian = ((color.hue()) % 360) * math.pi / 180
            self.hue_x = math.cos(radian) * self.half_width
            self.hue_y = math.sin(radian) * self.half_height
        self.scene.update()

    def rectToParam(self):
        if self.rectF == None:
            rect = QRectF(0, 0, 200, 200)
        else:
            rect = self.rectF

        self.width = rect.toRect().width()
        self.half_width = self.width / 2
        self.quarter_width = self.width / 4

        self.height = rect.toRect().height()
        self.half_height = self.height / 2
        self.quarter_height = self.height / 4

    @staticmethod
    def create_bg_pixmap(color1=None, color2=None):
        """
        :rtype: QPixmap
        """
        pixmap = QPixmap(QSize(16, 16))
        color1 = color1 or QColor(128, 128, 128)
        color2 = color2 or QColor(168, 168, 168)

        painter = QPainter(pixmap)
        painter.save()
        brush1 = QBrush(color1)
        brush2 = QBrush(color2)
        painter.fillRect(0, 0, 8, 8, brush1)
        painter.fillRect(8, 8, 8, 8, brush1)
        painter.fillRect(8, 0, 8, 8, brush2)
        painter.fillRect(0, 8, 8, 8, brush2)
        painter.restore()
        painter.end()

        return pixmap

    def sizeHint(self):
        return QSize(200, 200)
