#!/usr/bin/env python

'''
Provide EPICS motor controls for a beam line

.. figure:: mainwindow.png
    :alt: mainwindow.MainWindow
    :width: 60%

    Example mainwindow.MainWindow


'''


import os
import sys
from PyQt4.QtGui import *            #@UnusedWildImport
from PyQt4.QtCore import *           #@UnusedWildImport
import listpanel                      #@UnusedImport


class MainWindow(QMainWindow):
    
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        
        self.mlp = listpanel.MotorListPanel()
        self.setCentralWidget(self.mlp)
        
        self.dirty = False
        self.pvfile = ''

        self.createActions();
        self.createMenus();
        self.setStatus();
    
    def closeEvent(self, event):
        '''received a request to close application, shall we allow it?'''
        if self.dirty:
            event.ignore()
        else:
            event.accept()
    
    def createActions(self):
        '''define the actions for the GUI'''
        # TODO: needs File menu actions
        # TODO: needs Edit menu actions
        # TODO: needs Help menu actions
        
        self.action_open = QAction(self.tr('&Open'), None)
        self.action_open.setShortcut(QKeySequence.Open)
        self.action_open.setStatusTip(self.tr('Open a file with motor PVs'))
        self.action_open.triggered.connect(self.onOpenFile)
        
        self.action_exit = QAction(self.tr('E&xit'), None)
        self.action_exit.setShortcut(QKeySequence.Quit)
        self.action_exit.setStatusTip(self.tr('Exit the application'))
        self.action_exit.triggered.connect(self.close)
        
        self.action_NewPV = QAction(self.tr('New &PV'), None)
        self.action_NewPV.setShortcut('Ctrl+P')
        self.action_NewPV.setStatusTip(self.tr('Append a new motor PV to the list'))
        self.action_NewPV.triggered.connect(self.onNewPV)
   
    def createMenus(self):
        '''define the menus for the GUI'''
        fileMenu = self.menuBar().addMenu(self.tr('&File'))
        fileMenu.addAction(self.action_open)
        fileMenu.addSeparator()
        fileMenu.addAction(self.action_exit)
        
        # TODO: needs Edit menu
        
        pvMenu = self.menuBar().addMenu(self.tr('&PV'))
        pvMenu.addAction(self.action_NewPV)

        # TODO: needs Help menu
  
    def setStatus(self, message = 'Ready'):
        '''setup the status bar for the GUI or set a new status message'''
        self.statusBar().showMessage(self.tr(message))
    
    def onNewPV(self):
        '''add a new motor PV to the list'''
        # TODO:
        self.setStatus('feature not enabled yet')
    
    def onOpenFile(self):
        '''Choose a file with motor PVs'''
        fileName = str(QFileDialog().getOpenFileName(self))
        if len(fileName) > 0:
            self.setStatus('selected file: ' + fileName)
            self.loadFile(fileName)
            self.dirty = False
    
    def loadFile(self, filename):
        '''Open a file with motor PVs'''
        if os.path.exists(filename):
            self.pvfile = filename
            for pv in open(filename, 'r').readlines():
                self.mlp.addMotorPV(pv.strip())


def main():
    '''demo: display a GUI with motor PVs'''
    qapp = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(qapp.exec_())


if __name__ == '__main__':
    main()
