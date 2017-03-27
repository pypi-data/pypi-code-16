#!/usr/bin/env python

'''
provide a basic GUI for the APS EPICS Virtual Linac demo software

Copyright (c) 2009 - 2013, UChicago Argonne, LLC.
See LICENSE file for details.
'''


# - - - - - - - - - - - - - - - - - - Imports


import os
import sys
from PyQt4 import QtGui, QtCore

sys.path.insert(0, os.path.abspath('..'))
import bcdaqwidgets


# - - - - - - - - - - - - - - - - - - class


class DemoView(QtGui.QWidget):
    '''simple entry and label widgets for the most important PVs'''
    
    def __init__(self, parent=None, prefix='unknown'):
        QtGui.QWidget.__init__(self, parent)
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        self.setWindowTitle('Virtual Linac Controls')
        widget = QtGui.QLabel('Virtual Linac Controls')
        layout.addWidget(widget)
        widget.setAlignment(QtCore.Qt.AlignHCenter)
        sty = bcdaqwidgets.StyleSheet(widget, {'font':'bold 16px'})
        sty.updateStyleSheet()
        
        widget = bcdaqwidgets.BcdaQMomentaryButton()
        widget.ca_connect(prefix+':initAllSQ')
        widget.setText('Reset')
        widget.SetReleasedValue(1)
        layout.addWidget(widget)
        
        layout.addWidget(self.source(prefix))
        layout.addWidget(self.zone1(prefix))
        layout.addWidget(self.zone2(prefix))
        
        widget = bcdaqwidgets.BcdaQToggleButton()
        widget.ca_connect(prefix+':autoC')
        widget.SetReleasedValue(1)
        layout.addWidget(widget)
    
    def source(self, prefix):
        panel = QtGui.QGroupBox()
        layout = QtGui.QGridLayout()
        panel.setLayout(layout)
        panel.setFlat(True)
        panel.setTitle('source')
        
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        
        widget = QtGui.QLabel('cathode')
        layout.addWidget(widget, 0, 0)
        
        widget = bcdaqwidgets.BcdaQLineEdit()
        widget.ca_connect(prefix+':cathodeCurrentC')
        layout.addWidget(widget, 0, 1)
        
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect(prefix+':cathodeTempM')
        widget.useAlarmState = True
        layout.addWidget(widget, 0, 2)
        
        return panel
    
    def zone1(self, prefix):
        panel = QtGui.QGroupBox()
        layout = QtGui.QGridLayout()
        panel.setLayout(layout)
        panel.setFlat(True)
        panel.setTitle('zone 1')
        
        for col in range(1, 6):
            layout.setColumnStretch(col, 1)
        
        widget = QtGui.QLabel('CM')
        layout.addWidget(widget, 0, 0)
        
        widget = bcdaqwidgets.BcdaQToggleButton()
        layout.addWidget(widget, 0, 1, 1, 2)
        widget.ca_connect(prefix+':gunOnC')
        
        widget = bcdaqwidgets.BcdaQLabel()
        layout.addWidget(widget, 0, 3, 1, 2)
        widget.ca_connect(prefix+':gunOnC')
        widget.useAlarmState = True
        
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect(prefix+':CM1:intensityM')
        layout.addWidget(widget, 0, 5)
        
        for row in (1, 2):
            self.defineMagnetRow(prefix, row, row, layout)
        
        return panel
    
    def zone2(self, prefix):
        panel = QtGui.QGroupBox()
        layout = QtGui.QGridLayout()
        panel.setLayout(layout)
        panel.setFlat(True)
        panel.setTitle('zone 2')
        
        for col in range(1, 6):
            layout.setColumnStretch(col, 1)
        
        widget = QtGui.QLabel('GV1')
        layout.addWidget(widget, 0, 0)
        
        widget = bcdaqwidgets.BcdaQToggleButton()
        layout.addWidget(widget, 0, 1, 1, 2)
        widget.ca_connect(prefix+':GV1:positionC')
        
        widget = bcdaqwidgets.BcdaQLabel()
        layout.addWidget(widget, 0, 3, 1, 2)
        widget.ca_connect(prefix+':GV1:positionM')
        widget.useAlarmState = True
        
        for row in (3, 4, 5):
            self.defineMagnetRow(prefix, row, row-2, layout)
        
        return panel
    
    def defineMagnetRow(self, prefix, magnet_number, row, layout):
        widget = QtGui.QLabel('PM%d' % magnet_number)
        layout.addWidget(widget, row, 0)
    
        widget = bcdaqwidgets.BcdaQLineEdit()
        widget.ca_connect(prefix+':H%d:setCurrentC' % magnet_number)
        layout.addWidget(widget, row, 1)
        
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect(prefix+':PM%d:X:positionM' % magnet_number)
        widget.useAlarmState = True
        layout.addWidget(widget, row, 2)
        
        widget = bcdaqwidgets.BcdaQLineEdit()
        widget.ca_connect(prefix+':V%d:setCurrentC' % magnet_number)
        layout.addWidget(widget, row, 3)
        
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect(prefix+':PM%d:Y:positionM' % magnet_number)
        widget.useAlarmState = True
        layout.addWidget(widget, row, 4)
        
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect(prefix+':PM%d:intensityM' % magnet_number)
        layout.addWidget(widget, row, 5)


# - - - - - - - - - - - - - - - - - - methods

def main():
    '''demonstrate use of this module'''
    user = os.environ['USER']
    app = QtGui.QApplication(sys.argv)
    view = DemoView(prefix=user)
    view.show()
    sys.exit(app.exec_())


# - - - - - - - - - - - - - - - - - - main


if __name__ == '__main__':
    main()
