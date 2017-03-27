#!/usr/bin/env python

'''
Show one or more EPICS motor panels in a Qt GUI QWidget

.. figure:: multimotor.png
    :alt: multimotor.MotorMultiPanel
    :width: 60%

    Example multimotor.MotorMultiPanel

'''


import sys
from PyQt4.QtGui import *      #@UnusedWildImport
import motor_qt


class MotorMultiPanel(QFrame):
    '''
    horizontal panel of multiple MotorPanel() objects
    
    USAGE::

        panel = MotorMultiPanel()
        panel.connect(['como:m1', 'como:m2', 'como:m3'])

    '''

    def __init__(self, parent=None, pvlist=None):
        super(MotorMultiPanel, self).__init__(parent)
        
        self.layout = QHBoxLayout()

        self.setLayout(self.layout)
        self.setWindowTitle("MultiMotor panel")

        if pvlist is not None:
            self.connect(pvlist)
    
    def connect(self, motor_pv_list=[]):
        '''connect the MotorPanel widgets with their motor PVs'''
        self.motors = []
        for pvname in motor_pv_list:
            panel = motor_qt.MotorPanel(self)
            self.layout.addWidget(panel)
            self.motors.append(panel)
            panel.connect(pvname)
        if len(motor_pv_list) > 0:
            self.setWindowTitle("motor%dx" % len(motor_pv_list))
    
    def disconnect(self):
        '''disconnect all the PVs in all MotorPanel objects in the panel'''
        [motor.disconnect() for motor in self.motors]


def main():
    '''demo: display the named motors in a horizontal block'''
    if len(sys.argv) < 2:
        raise RuntimeError, "usage %s motor [motor ...]" % sys.argv[0]
    app = QApplication(sys.argv)
    panel = MotorMultiPanel(pvlist=sys.argv[1:])
    #panel.connect()
    panel.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
