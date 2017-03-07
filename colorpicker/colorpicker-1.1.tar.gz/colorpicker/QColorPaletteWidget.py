# coding:utf-8
from __future__ import division, print_function, unicode_literals, absolute_import
# noinspection PyUnresolvedReferences
from future_builtins import *

from PySide.QtGui import *
from PySide.QtCore import *

import copy


#
# view
#
class QColorPaletteWidget(QGraphicsView):
    colorChanged = Signal(str)

    def __init__(self, parent=None):
        super(QColorPaletteWidget, self).__init__(parent)
        self.screen_scene = QGraphicsScene(self)
        self.setScene(self.screen_scene)
        self.bg_brush = QBrush(self.create_bg_pixmap())
        self.color = palette_color[-1]

        self.resize(180 + 2, 100 + 2)

        pal_iter = iter(palette_color)
        for _x in range(9):
            for _y in range(5):
                color = pal_iter.next()
                picker = QGraphicsPaletteItem()
                picker.setup(self, _x, _y, color)
                self.screen_scene.addItem(picker)

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

    def drawBackground(self, painter, rect):
        """
        :type rect: QRectF
        :type painter: QPainter
        """
        painter.save()
        painter.fillRect(rect, self.bg_brush)
        painter.restore()

    def setColor(self, color):
        self.color = QColor(color)

    def getColor(self):
        return(self.color)

    def selectColor(self, color):
        self.color = copy.deepcopy(color)
        self.colorChanged.emit('colorChanged')

#
# Palette Draw
#
class QGraphicsPaletteItem(QGraphicsItem):
    def setup(self, parent, x, y, color, size=20):
        self.parent = parent
        self.color = color
        self.rect = QRect(size * x, size * y, size, size)
        # self.setRect(self.rect)

        if x == 0 and y == 0:
            self.text = ""
        elif x == 0:
            self.text = str(y - 1)
        elif y == 0:
            self.text = str(x - 1)
        else:
            self.text = ""

    def boundingRect(self, *args, **kwargs):
        return(QRectF(self.rect))

    def paint(self, painter, option, widget):
        if self.color == None:
            painter.setBrush(QPalette().brush(QPalette.Midlight))
            painter.drawRect(self.rect)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawText(self.rect, self.text, QTextOption(Qt.AlignVCenter | Qt.AlignHCenter))
        else:
            painter.setBrush(QBrush(self.color))
            painter.drawRect(self.rect)

    def mousePressEvent(self, event):
        if self.color != None:
            if event.button() == Qt.RightButton:
                self.color = copy.deepcopy(self.parent.color)
                self.update()
            elif event.button() == Qt.LeftButton:
                self.parent.selectColor(self.color)

palette_color = [
	None,
	None,
	None,
	None,
	None,

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(255, 0, 0, 255),
    QColor(190, 0, 0, 255),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(0, 255, 0, 255),
    QColor(0, 190, 0, 255),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(0, 0, 255, 255),
    QColor(0, 0, 190, 255),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(255, 255, 0, 255),
    QColor(190, 190, 0, 255),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(0, 255, 255, 255),
    QColor(0, 190, 190, 255),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(255, 0, 255, 255),
    QColor(190, 0, 190, 255),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 255),
    QColor(190, 190, 190, 200),

	None,
    QColor(255, 255, 255, 0),
    QColor(255, 255, 255, 0),
    QColor(255, 70, 255, 200),
    QColor(190, 130, 190, 150),
]

