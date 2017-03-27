#!/usr/bin/env python

'''
PyQt4 implementation of EPICS probe

:author: Matt Newville, CARS, University of Chicago
:note: Does not use bcdaqwidgets
'''

import epics
import os
import sys
from PyQt4.QtGui import QWidget, QLabel, QLineEdit, QGridLayout, QApplication

class PVProbe(QWidget):
    '''frame that monitors a user-entered EPICS PV'''
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        name_label  = QLabel("PV Name:")
        self.pvname = QLineEdit()
        value_label = QLabel("PV Value:")
        self.value  = QLabel(" "*4)

        self.pvname.returnPressed.connect(self.onPVNameReturn)
        self.pv = None

        grid = QGridLayout()
        grid.addWidget(name_label,   0, 0)
        grid.addWidget(self.pvname,  0, 1)
        grid.addWidget(value_label,  1, 0)
        grid.addWidget(self.value,   1, 1)

        self.setLayout(grid)
        self.setWindowTitle("PyQt4 PV Probe:")

    def onPVNameReturn(self):
        '''responds when user enters a new PV'''
        if self.pv is not None:
            self.pv.remove_callback()
            self.pv.ca_disconnect()
        self.pv = epics.PV(str(self.pvname.text()), callback=self.onPVChange)

    def onPVChange(self, pvname=None, char_value=None, **kws):
        '''updates the widget (not thread-safe)'''
        self.value.setText(char_value)


def main():
    app = QApplication(sys.argv)
    probe = PVProbe()
    probe.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
