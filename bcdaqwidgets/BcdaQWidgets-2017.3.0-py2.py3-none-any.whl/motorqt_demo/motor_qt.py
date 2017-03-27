#!/usr/bin/env python

'''
Show an EPICS motor in a Qt GUI QWidget

.. figure:: motor_qt.png
    :alt: motor_qt.MotorPanel

    Example motor_qt.MotorPanel

'''


# TODO: show LVIO somehow, perhaps setting VAL.background = yellow?


import epics
import sys
from PyQt4.QtGui import *      #@UnusedWildImport


BLANK = ' '*4
BACKGROUND_DEFAULT = '#efefef'
#BACKGROUND_DONE_MOVING = 'beige'
BACKGROUND_DONE_MOVING = BACKGROUND_DEFAULT
BACKGROUND_MOVING = 'lightgreen'
BACKGROUND_LVIO_ON = 'yellow'
BACKGROUND_LIMIT_ON = 'red'
TOOLTIPS = {
        'DESC': 'DESC: short description',
        'NAME': 'NAME: EPICS PV name',
        'RBV':  'RBV: motor readback value',
        'VAL':  'VAL: motor target value',
        'EGU':  'EGU: engineering units',
        'STOP': 'STOP: command this motor to stop moving',
        'TWV':  'TWV: tweak value',
        'TWF':  'TWF: increment motor by tweak value',
        'TWR':  'TWR: decrement motor by tweak value',
        '*10':  'multiply tweak value by 10',
        '/10':  'divide tweak value by 10',
}
STYLES = {      ### http://doc.qt.digia.com/qt/stylesheet-reference.html
    'self': '''
             MotorPanel { 
                border-style: solid;
                border-color: black;
                border-width: 1px;
             }
            ''',
    'DESC': '''
             QLabel { 
                qproperty-alignment: AlignCenter;
                color: white; 
                background-color: blue;
                font: bold;
             }
            ''',
    'NAME': '''
             QLabel { 
                qproperty-alignment: AlignCenter;
                color: darkblue; 
                background-color: lightgray;
                font: bold;
             }
            ''',
    'RBV': '''
             QLabel { 
                qproperty-alignment: AlignCenter;
             }
            ''',
    'EGU': '''
             QLabel { 
                qproperty-alignment: AlignCenter;
             }
            ''',
    'VAL': '''
            QLineEdit { 
                   background-color: beige;
                   text-align: left;
                   }
           ''',
    'STOP': '''
            QPushButton { 
                   background-color: red;
                   color: black;
                   text-align: center;
                   }
            QPushButton:hover { 
                   background-color: red;
                   color: yellow;
                   font: bold;
                   text-align: center;
                   }
            ''',
    'TWV': '''
            QLineEdit { 
                   background-color: lightgray;
                   text-align: left;
                   }
           ''',
    'TWF': '''
            QPushButton { 
                   width: 20px;
                   min-width: 20px;
                   max-width: 20px;
                   }
           ''',
    'TWR': '''
            QPushButton { 
                   width: 20px;
                   min-width: 20px;
                   max-width: 20px;
                   }
           ''',
    '*10': '''
            QPushButton { 
                   width: 20px;
                   min-width: 20px;
                   max-width: 20px;
                   }
           ''',
    '/10': '''
            QPushButton { 
                   width: 20px;
                   min-width: 20px;
                   max-width: 20px;
                   }
           ''',
}


class MotorPanel(QFrame):
    '''
    Basic GUI for one EPICS motor pv
    
    USAGE::

        panel = MotorPanel()
        panel.connect('como:m1')
        ...
        panel.connect('como:m2')    # changes the panel to a different PV
        ...
        panel.disconnect()

    '''
    
    def __init__(self, parent=None, pvname=None):
        super(MotorPanel, self).__init__(parent)
        QToolTip.setFont(QFont('SansSerif', 10))
        
        self.create_GUI()
        self.apply_styles()
        self.create_actions()
        
        if isinstance(pvname, str):
            self.connect(pvname)

    def create_GUI(self):
        '''define controls AND set the layout'''    
        self.controls = {}
        for field in ['DESC', 'NAME', 'EGU', 'RBV']:
            self.controls[field] = QLabel(BLANK)
        self.controls['VAL'] = QLineEdit()
        self.controls['STOP'] = QPushButton('STOP')
        self.controls['TWF'] = QPushButton('>')
        self.controls['TWV'] = QLineEdit()
        self.controls['TWR'] = QPushButton('<')
        self.controls['*10'] = QPushButton('*')
        self.controls['/10'] = QPushButton('/')
        self.pv = None
        self.controls['RBV'].setAutoFillBackground(True)
        self.setLabelBackground(self.controls['RBV'], BACKGROUND_DONE_MOVING)
        
        layout = QVBoxLayout()
        for field in ['DESC', 'NAME', 'EGU', 'RBV', 'VAL']:
            layout.addWidget(self.controls[field])
        
        tweak_frame = QFrame(self)
        tweak_layout = QHBoxLayout()
        for field in ['TWR', '/10', 'TWV', '*10', 'TWF']:
            tweak_layout.addWidget(self.controls[field])
        tweak_frame.setLayout(tweak_layout)
        layout.addWidget(tweak_frame)
        
        layout.addWidget(self.controls['STOP'])

        self.setLayout(layout)
        self.setWindowTitle("Motor panel")

    def apply_styles(self):
        '''apply styles and tips'''     
        for field in ['DESC', 'NAME', 'EGU', 'RBV', 'VAL', 
                      'STOP', 'TWV', 'TWF', 'TWR', '*10', '/10']:
            if field in STYLES:
                self.controls[field].setStyleSheet(STYLES[field])
            if field in TOOLTIPS:
                self.controls[field].setToolTip(TOOLTIPS[field])
        
        self.setStyleSheet(STYLES['self'])

    def create_actions(self):
        '''define actions'''
        self.controls['VAL'].returnPressed.connect(self.onReturnVAL)
        self.controls['TWV'].returnPressed.connect(self.onReturnTWV)
        self.controls['TWR'].clicked.connect(self.onPushTWR)
        self.controls['TWF'].clicked.connect(self.onPushTWF)
        self.controls['*10'].clicked.connect(self.onPush10x)
        self.controls['/10'].clicked.connect(self.onPush_1x)
        self.controls['STOP'].clicked.connect(self.onPushSTOP)

    def connect(self, pvname=None):
        '''connect this panel with an EPICS motor PV'''
        if pvname is None:
            raise RuntimeError, "lbl_name must not be 'None'"
        if len(pvname) == 0:
            raise RuntimeError, "lbl_name must not be ''"
        
        if self.pv is not None:
            self.disconnect()
        
        self.motor_pv = pvname.split('.')[0]   # keep everything to left of first dot
        
        self.controls['NAME'].setText(self.motor_pv)
        self.pv = epics.Motor(str(self.motor_pv))   # verifies that self.motor_pv has RTYP='motor'

        callback_dict = {
            #field:  callback function
            'DESC': self.onChangeDESC,
            'EGU':  self.onChangeEGU,
            'RBV':  self.onChangeRBV,
            'VAL':  self.onChangeVAL,
            'TWV':  self.onChangeTWV,
            'DMOV': self.onChangeDMOV,
            'HLS':  self.onChangeHLS,
            'LLS':  self.onChangeLLS,
        }
        for field, func in callback_dict.iteritems():
            self.pv.set_callback(attr=field, callback=func)

        self.controls['DESC'].setText(self.pv.description)
        self.controls['EGU'].setText(self.pv.units)
        
        # display initial values
        self.onChangeRBV(value=self.pv.get('RBV'))
        self.onChangeVAL(value=self.pv.get('VAL'))
        self.onChangeTWV(value=self.pv.get('TWV'))
        self.onChangeDMOV(value=self.pv.get('DMOV'))

    def disconnect(self):
        '''disconnect this panel from EPICS'''
        if self.pv is not None:
            for field in ['VAL', 'RBV', 'DESC', 'EGU', 'TWV', 'DMOV', 'HLS', 'LLS']:
                self.pv.clear_callback(attr=field)
            #self.pv.disconnect()   # There is no disconnect() method!
            self.pv = None
            for field in ['DESC', 'NAME', 'EGU', 'RBV', 'VAL', 'TWV']:
                self.controls[field].setText(BLANK)

    def closeEvent(self, event):
        '''be sure to disconnect from EPICS when closing'''
        self.disconnect()

    def onPushSTOP(self):
        '''stop button was pressed'''
        if self.pv is not None:
            self.pv.stop()

    def onPushTWF(self):
        '''tweak forward button was pressed'''
        if self.pv is not None:
            self.pv.put('TWF', 1)

    def onPushTWR(self):
        '''tweak reverse button was pressed'''
        if self.pv is not None:
            self.pv.put('TWR', 1)

    def onPush10x(self):
        '''multiply TWV*10 button was pressed'''
        if self.pv is not None:
            self.pv.put('TWV', 10*self.pv.get('TWV'))

    def onPush_1x(self):
        '''multiply TWV*0.1 button was pressed'''
        if self.pv is not None:
            self.pv.put('TWV', 0.1*self.pv.get('TWV'))

    def onReturnTWV(self):
        '''new target value was entered in this panel'''
        if self.pv is not None:
            number = float(self.controls['TWV'].text())
            self.pv.put('TWV', number)

    def onReturnVAL(self):
        '''new target value was entered in this panel'''
        if self.pv is not None:
            number = float(self.controls['VAL'].text())
            self.pv.move(number)

    def onChangeDESC(self, char_value=None, **kws):
        '''EPICS monitor on DESC called this'''
        self.controls['DESC'].setText(char_value)

    def onChangeDMOV(self, value = None, **kws):
        '''EPICS monitor on DMOV called this, change the color of the RBV label'''
        if value is not None:
            color = {1: BACKGROUND_DONE_MOVING, 0: BACKGROUND_MOVING}[value]
            self.setLabelBackground(self.controls['RBV'], color)

    def onChangeHLS(self, value=None, **kws):
        '''EPICS monitor on HLS called this, change the color of the TWF button'''
        if value is not None:
            color = {0: BACKGROUND_DEFAULT, 0: BACKGROUND_LIMIT_ON}[value]
            self.setLabelBackground(self.controls['TWF'], color)

    def onChangeLLS(self, value=None, **kws):
        '''EPICS monitor on LLS called this, change the color of the TWR button'''
        if value is not None:
            color = {0: BACKGROUND_DEFAULT, 0: BACKGROUND_LIMIT_ON}[value]
            self.setLabelBackground(self.controls['TWR'], color)

    def onChangeEGU(self, char_value=None, **kws):
        '''EPICS monitor on EGU called this'''
        self.controls['EGU'].setText(char_value)

    def onChangeRBV(self, value=None, **kws):
        '''EPICS monitor on RBV called this'''
        if value is not None:
            fmt = "%%.%df" % self.pv.get('PREC')
            self.controls['RBV'].setText(fmt % value)

    def onChangeTWV(self, value=None, **kws):
        '''EPICS monitor on TWV called this'''
        if value is not None:
            fmt = "%%.%df" % self.pv.get('PREC')
            self.controls['TWV'].setText(fmt % value)

    def onChangeVAL(self, value=None, **kws):
        '''EPICS monitor on VAL called this'''
        if value is not None:
            fmt = "%%.%df" % self.pv.get('PREC')
            self.controls['VAL'].setText(fmt % value)

    def setLabelBackground(self, widget = None, color = BACKGROUND_DEFAULT):
        '''change the background color of a Qt widget'''
        if widget is not None:
            palette = QPalette()
            palette.setColor(widget.backgroundRole(), QColor(color))
            widget.setPalette(palette)


def main():
    '''demo: display the named motors in a horizontal block'''
    if len(sys.argv) != 2:
        raise RuntimeError, "usage: %s motor" % sys.argv[0]
    app = QApplication(sys.argv)
    panel = MotorPanel(pvname=sys.argv[1])
    #panel.connect()
    panel.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
