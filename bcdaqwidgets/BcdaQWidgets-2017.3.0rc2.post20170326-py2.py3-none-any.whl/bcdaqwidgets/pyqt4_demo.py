#!/usr/bin/env python

'''
demonstrate bcdaqwidgets with PyQt4
'''


import os
from PyQt4 import QtCore, QtGui
import epics
import bcdaqwidgets


class DemoView(QtGui.QWidget):
    '''
    Show the BcdaQWidgets using an EPICS PV connection.

    Allow it to connect and ca_disconnect.
    This is a variation of EPICS PV Probe.
    '''

    def __init__(self, parent=None, pvname=None):
        QtGui.QWidget.__init__(self, parent)

        self.sig = bcdaqwidgets.BcdaQSignalDef()
        self.sig.newBgColor.connect(self.SetBackgroundColor)
        self.toggle = False

        layout = QtGui.QFormLayout()
        self.setLayout(layout)

        lbl  = QtGui.QLabel('PV')
        wid = QtGui.QLabel(str(pvname))
        layout.addRow(lbl, wid)

        self.value = bcdaqwidgets.BcdaQLabel()
        layout.addRow(QtGui.QLabel('BcdaQLabel'), self.value)

        self.setWindowTitle("Demo bcdaqwidgets module")
        if pvname is not None:
            self.ca_connect(pvname)

            lbl = QtGui.QLabel('BcdaQLabel with alarm colors')
            wid = bcdaqwidgets.BcdaQLabel(pvname=pvname, useAlarmState=True)
            layout.addRow(lbl, wid)

            lbl = QtGui.QLabel('RBV_BcdaQLabel')
            wid = bcdaqwidgets.RBV_BcdaQLabel()
            wid.ca_connect(pvname+'.RBV')
            layout.addRow(lbl, wid)

            lbl = QtGui.QLabel('BcdaQLineEdit')
            wid = bcdaqwidgets.BcdaQLineEdit(pvname=pvname)
            layout.addRow(lbl, wid)

            lbl = QtGui.QLabel('BcdaQLineEdit')
            wid = bcdaqwidgets.BcdaQLineEdit(pvname=pvname + '.TWV')
            layout.addRow(lbl, wid)

            pvname = pvname.split('.')[0] + '.TWF'
            lbl = QtGui.QLabel('BcdaQMomentaryButton')
            wid = bcdaqwidgets.BcdaQMomentaryButton(label='tweak +', pvname=pvname + '.TWF')
            wid.SetPressedValue(1)
            layout.addRow(lbl, wid)

            pvname = pvname.split('.')[0] + '.TWR'
            lbl = QtGui.QLabel('BcdaQMomentaryButton')
            wid = bcdaqwidgets.BcdaQMomentaryButton(label='tweak -', pvname=pvname + '.TWR')
            wid.SetPressedValue(1)
            layout.addRow(lbl, wid)

    def ca_connect(self, pvname):
        self.value.ca_connect(pvname, ca_callback=self.callback)

    def callback(self, *args, **kw):
        self.sig.newBgColor.emit()   # threadsafe update of the widget

    def SetBackgroundColor(self, *args, **kw):
        '''toggle the background color of self.value via its stylesheet'''
        self.toggle = not self.toggle
        color = {False: "#ccc333", True: "#cccccc",}[self.toggle]
        self.value.updateStyleSheet({'background-color': color})


#------------------------------------------------------------------


def main():
    '''command-line interface to test this GUI widget'''
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Test the bcdaqwidgets module')

    # positional arguments
    # not required if GUI option is selected
    parser.add_argument('test_PV', 
                        action='store', 
                        nargs='?',
                        help="EPICS PV name", 
                        default="xxx:m1", 
                        )
    results = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    view = DemoView(pvname=results.test_PV)
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
