#!/usr/bin/env python

'''
Provide controls for one or more EPICS motors

.. figure:: listpanel.png
    :alt: listpanel.MotorListPanel

    Example listpanel.MotorListPanel



Future Features
==================

* consider showing the PV.DESC values (2-col list, sort by either col)
* consider showing which PVs are currently available
* need a "removeMotorPV" method
* need a "listMotorPVs" method
* need a "sortList" method

'''


import motor_qt
import sys
from PyQt4.QtGui import *      #@UnusedWildImport


class MotorListPanel(QFrame):
    '''
    GUI for a list of EPICS motor PVs
    '''
    
    def __init__(self, parent=None):
        super(MotorListPanel, self).__init__(parent)
        
        self.motor_list = QStandardItemModel()
    
        listview = QListView()
        listview.setModel(self.motor_list)
        
        self.motor_panel = motor_qt.MotorPanel()

        splitter = QSplitter(self)
        splitter.addWidget(listview)
        splitter.addWidget(self.motor_panel)
        
        listview.clicked.connect(self.onListviewClick)
        
        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def addMotorPV(self, motor_pv = None):
        '''add a motor PV name to the QListView panel'''
        if motor_pv is None:
            raise RuntimeError, "must call addMotorPV() with PV name string!"
        if not isinstance(motor_pv, str):
            raise RuntimeError, "motor_pv must be a string"
        if len(motor_pv) < 2:
            raise RuntimeError, "motor_pv must be more than 1 character"
        self.motor_list.appendRow(QStandardItem(motor_pv))
    
    def onListviewClick(self, index):
        '''a motor PV was clicked on, show it in the MotorPanel'''
        pv = self.motor_list.itemFromIndex(index).text()
        self.motor_panel.connect(pv)


def main():
    '''demo: display the named motors in a list'''
    if len(sys.argv) < 2:
        raise RuntimeError, "usage %s motor [motor ...]" % sys.argv[0]
    app = QApplication(sys.argv)
    panel = MotorListPanel()
    for item in sys.argv[1:]:
        panel.addMotorPV(item)
    panel.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    for m in range(8):
        sys.argv.append('xxx:m%d' % (m+1))
    main()
