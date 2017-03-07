"""QColorBarWidget"""
# coding:utf-8
from __future__ import division, print_function, unicode_literals, absolute_import
# noinspection PyUnresolvedReferences
from future_builtins import *

from PySide.QtGui import *
from PySide.QtCore import *

# colorbar type
BAR_TYPE_HUE = 0
BAR_TYPE_SATURATION = 1
BAR_TYPE_VALUE = 2
BAR_TYPE_ALPHA = 3
BAR_TYPE_MAX = 4

Lupe_Color = [
    QColor(0, 0, 0, 255),
    QColor(0, 0, 0, 255),
    QColor(255, 255, 255, 255),
    QColor(255, 0, 0, 255)
]


class QColorBarWidget(QGraphicsView):
    colorChanged = Signal(str)

    def __init__(self, parent, type=BAR_TYPE_HUE):
        super(QColorBarWidget, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.width = 0

        self.type = type if type < BAR_TYPE_MAX else BAR_TYPE_HUE
        self.lupe_color = Lupe_Color[type]

        self.color = QColor()
        self.color.setHsv(0, 255, 255, 255)
        self.setColor(self.color)

        # bg tile
        pixmap = QPixmap(QSize(16, 16))
        tile = QPainter(pixmap)
        tile.save()
        brush1 = QBrush(QColor(128, 128, 128))
        brush2 = QBrush(QColor(168, 168, 168))
        tile.fillRect(0, 0, 8, 8, brush1)
        tile.fillRect(8, 8, 8, 8, brush1)
        tile.fillRect(8, 0, 8, 8, brush2)
        tile.fillRect(0, 8, 8, 8, brush2)
        tile.restore()
        tile.end()
        self.bg_brush = QBrush(pixmap)

        self.setMinimumHeight(20)
        self.setFixedHeight(20)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def drawBackground(self, painter, rect):
        """
        :type rect: QRectF
        :type painter: QPainter
        """
        painter.save()
        painter.fillRect(rect, self.bg_brush)
        painter.restore()

    def drawForeground(self, painter, rect):
        """
        :type rect: QRectF
        :type painter: QPainter
        """
        painter.save()
        painter.translate(rect.center())
        painter.setRenderHint(QPainter.Antialiasing, True)
        self.width = rect.toRect().width()
        half_width = self.width / 2
        height = rect.toRect().height()
        half_height = height / 2
        # bar
        gradient = QLinearGradient(-half_width, 0, half_width, 0)
        self.makeGradient(gradient)
        painter.setBrush(gradient)
        painter.drawRect(-half_width, -half_height, self.width, height)
        # lupe
        painter.setPen(QPen(self.lupe_color, 1))
        painter.setBrush(QColor(0, 0, 0, 0))
        half_width = self.px - half_width
        painter.drawEllipse(half_width - 2, 2 - half_height, 5, 5)
        painter.fillRect(half_width, 6 - half_height, 1, height, QBrush(self.lupe_color))

        painter.restore()

    def mouseMoveEvent(self, event):
        self.clickToColor(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clickToColor(event)

    def clickToColor(self, event):
        self.px = event.pos().x()
        param = self.px / self.width
        param = 0 if param < 0 else param
        if self.type == BAR_TYPE_HUE:
            self.color.setHsv(360 * param, self.color.saturation(), self.color.value(), self.color.alpha())
        elif self.type == BAR_TYPE_SATURATION:
            self.color.setHsv(self.color.hue(), 255 * param, self.color.value(), self.color.alpha())
        elif self.type == BAR_TYPE_VALUE:
            self.color.setHsv(self.color.hue(), self.color.saturation(), 255 * param, self.color.alpha())
        else:  # alpha
            self.color.setAlphaF(param)

        self.colorChanged.emit('colorChanged')
        self.scene.update()

    def getColor(self):
        return (self.color)

    def setColor(self, color):
        self.color = QColor(color)
        if self.type == BAR_TYPE_HUE:
            self.px = color.hue() * self.width / 360
        elif self.type == BAR_TYPE_SATURATION:
            self.px = color.saturation() * self.width / 255
        elif self.type == BAR_TYPE_VALUE:
            self.px = color.value() * self.width / 255
        else:  # alpha
            self.px = color.alpha() * self.width / 255
        self.scene.update()

    def makeGradient(self, gradient):
        color = QColor()
        if self.type == BAR_TYPE_HUE:
            for _ in range(11):
                color.setHsv(_ * 36, 255, 255, 255)
                gradient.setColorAt(0.1 * _, color)
        elif self.type == BAR_TYPE_SATURATION:
            color.setHsv(360, 0, 255, 255)
            gradient.setColorAt(0.0, color)
            color.setHsv(360, 255, 255, 255)
            gradient.setColorAt(1.0, color)
        elif self.type == BAR_TYPE_VALUE:
            color.setHsv(360, 255, 0, 255)
            gradient.setColorAt(0.0, color)
            color.setHsv(360, 255, 255, 255)
            gradient.setColorAt(1.0, color)
        else:  # alpha
            color.setRgb(255, 255, 255, 0)
            gradient.setColorAt(0.0, color)
            color.setRgb(255, 255, 255, 255)
            gradient.setColorAt(1.0, color)
        return

    def sizeHint(self):
        return QSize(200, 20)
