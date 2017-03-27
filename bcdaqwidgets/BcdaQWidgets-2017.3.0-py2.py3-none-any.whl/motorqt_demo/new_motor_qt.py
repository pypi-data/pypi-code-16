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
import bcdaqwidgets


BLANK = ' '*4
BACKGROUND_DEFAULT = '#efefef'
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
             BcdaQLabel { 
                qproperty-alignment: AlignCenter;
                color: white; 
                background-color: blue;
                font: bold;
             }
            ''',
    'NAME': '''
             BcdaQLabel { 
                qproperty-alignment: AlignCenter;
                color: darkblue; 
                background-color: lightgray;
                font: bold;
             }
            ''',
    'RBV': '''
             BcdaQLabel_RBV { 
                qproperty-alignment: AlignCenter;
             }
            ''',
    'EGU': '''
             BcdaQLabel { 
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
            BcdaQMomentaryButton { 
                   background-color: red;
                   color: black;
                   font: bold;
                   text-align: center;
                   }
            BcdaQMomentaryButton:hover { 
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


class MotorPanel(QWidget):
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
        for field in ['DESC', 'NAME', 'EGU',]:
            self.controls[field] = bcdaqwidgets.BcdaQLabel()
        for field in ['VAL', 'TWV',]:
            self.controls[field] = bcdaqwidgets.BcdaQLineEdit()
        self.controls['RBV'] = bcdaqwidgets.BcdaQLabel_RBV()
        for label, field in {'Stop':'STOP', '>':'TWF', '<':'TWR'}.items():
            self.controls[field] = bcdaqwidgets.BcdaQMomentaryButton(label)
        for label, field in {'*':'*10', '/':'/10'}.items():
            self.controls[field] = QPushButton(label)
        self.pv = None

        for field in ['STOP', 'TWF', 'TWR',]:
            self.controls[field].SetPressedValue(1)
        
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
        for field in ['*10', '/10']:
            if field in STYLES:
                self.controls[field].setStyleSheet(STYLES[field])
            if field in TOOLTIPS:
                self.controls[field].setToolTip(TOOLTIPS[field])
        
        # FIXME: none of these bcdaqwidgets styles are working!
        # This fix requires revision in the StyleSheet class algorithm
        # The assumed underlying model is too flat for the STOP button, for example.  Needs a :hover aspect.
        for field in ['STOP', 'TWF', 'TWR', 'DESC', 'NAME', 'EGU']:
            if field in STYLES:
                self.controls[field].setStyleSheet(STYLES[field])
        
        self.setStyleSheet(STYLES['self'])

    def create_actions(self):
        '''define actions'''
        self.controls['*10'].clicked.connect(self.onPush10x)
        self.controls['/10'].clicked.connect(self.onPush_1x)

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
        self.pv = epics.Motor(self.motor_pv)   # verifies that self.motor_pv has RTYP='motor'

        callback_dict = {
            #field:  callback function
            'HLS':  self.onChangeHLS,
            'LLS':  self.onChangeLLS,
        }
        for field, func in callback_dict.iteritems():
            self.pv.set_callback(attr=field, callback=func)
        
        for field in ['DESC', 'NAME', 'EGU', 'VAL', 'RBV', 'TWV', 'STOP', 'TWF', 'TWR', ]:
            self.controls[field].ca_connect(pvname + '.' + field)

    def disconnect(self):
        '''disconnect this panel from EPICS'''
        if self.pv is not None:
            for field in ['HLS', 'LLS']:
                self.pv.clear_callback(attr=field)
            for field in ['DESC', 'NAME', 'EGU', 'VAL', 'RBV', 'TWV', 'TWF', ]:
                self.controls[field].ca_disconnect()

            self.pv = None
            for field in ['DESC', 'NAME', 'EGU', 'RBV', 'VAL', 'TWV', ]:
                self.controls[field].setText(BLANK)

    def closeEvent(self, event):
        '''be sure to disconnect from EPICS when closing'''
        self.disconnect()

    def onPush10x(self):
        '''multiply TWV*10 button was pressed'''
        if self.pv is not None:
            self.pv.put('TWV', 10*self.pv.get('TWV'))

    def onPush_1x(self):
        '''multiply TWV*0.1 button was pressed'''
        if self.pv is not None:
            self.pv.put('TWV', 0.1*self.pv.get('TWV'))

    def onChangeHLS(self, value=None, **kws):
        '''EPICS monitor on HLS called this, change the color of the TWF button'''
        if value is not None:
            color = {0: BACKGROUND_DEFAULT, 1: BACKGROUND_LIMIT_ON}[value]
            self.setLabelBackground(self.controls['TWF'], color)

    def onChangeLLS(self, value=None, **kws):
        '''EPICS monitor on LLS called this, change the color of the TWR button'''
        if value is not None:
            color = {0: BACKGROUND_DEFAULT, 1: BACKGROUND_LIMIT_ON}[value]
            self.setLabelBackground(self.controls['TWR'], color)

    def setLabelBackground(self, widget = None, color = BACKGROUND_DEFAULT):
        '''change the background color of a Qt widget'''
        if widget is not None:
            palette = QPalette()
            palette.setColor(widget.backgroundRole(), color)
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
    sys.argv.append('prj:m1')
    main()
