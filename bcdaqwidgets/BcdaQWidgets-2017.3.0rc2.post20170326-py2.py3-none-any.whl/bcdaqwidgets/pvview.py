#!/usr/bin/env python

'''display one or more EPICS PVs in a PyQt4 GUI window as a table'''

import os
import sys
from PyQt4.QtGui import QWidget, QLabel, QGridLayout, QApplication
sys.path.insert(0, os.path.abspath('..'))
import bcdaqwidgets


class PVView(QWidget):
    ''' '''
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.db = {}

        name_label  = QLabel("PV Name")
        value_label = QLabel("PV Value")
        for item in (name_label, value_label):
            sty = bcdaqwidgets.StyleSheet(item, {
                                   'background-color': 'gray',
                                   'color': 'white',
                                   'font': 'bold',
                                   })
            sty.updateStyleSheet()

        self.grid = QGridLayout()
        self.grid.addWidget(name_label,   0, 0)
        self.grid.addWidget(value_label,  0, 1)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)

        self.setLayout(self.grid)
        self.setWindowTitle("EPICS PV View")

    def add(self, pvname):
        '''add a PV to the table'''
        if pvname in self.db:
            return
        row = len(self.db) + 1
        label = QLabel(pvname)
        widget = bcdaqwidgets.BcdaQLabel(pvname=pvname)
        widget.useAlarmState = True
        self.db[pvname] = widget
        self.grid.addWidget(label, row, 0)
        self.grid.addWidget(widget, row, 1)


def main():
    app = QApplication(sys.argv)
    probe = PVView()
    if len(sys.argv) < 2:
        raise RuntimeError, "Must specify one or more EPICS PVs on command line"
    for pvname in sys.argv[1:]:
        probe.add(pvname)
    probe.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
