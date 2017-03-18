#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 15:28:14 2016

@author: Robert A. McLeod
"""

import os, os.path, glob, sys
from PySide import QtGui, QtCore
# import functools
from . import ui_junker
import multiprocessing as mp
import mrcz
import cytoolz
import skimage.io
import scipy.ndimage as ni
import zorro.zorro_util as util
import numpy as np
import time


class keyFilter(QtCore.QObject):
    
    def __init__(self, Window):
        self.eventCounter = 0
        QtCore.QObject.__init__(self)
        self.Window = Window
        
    def eventFilter(self, obj, event):
        # Why do I get two key presses???

            
        if (event.type() == QtCore.QEvent.KeyPress):
            #if event.isAutoRepeat():
            #    return
            
            self.eventCounter += 1
            key = event.key()
            # print( "%d: Received key %s " % (self.eventCounter, key) )
            
            if key == QtCore.Qt.Key_Right:
                self.Window.incrementIndex()
            elif key == QtCore.Qt.Key_Left:
                self.Window.decrementIndex()
            elif key == QtCore.Qt.Key_Delete or key == QtCore.Qt.Key_Space:
                self.Window.junkCurrent()
            elif key == QtCore.Qt.Key_Z:
                self.Window.undoCurrent()
            elif key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_S:
                self.Window.salvageCurrent()
                
        return QtGui.QWidget.eventFilter( self, obj, event )
        
        
def batchProcPNG( mrcNames ):
    for mrcName in mrcNames:
        print( "Converting %s to PNG format" % mrcName )
        pngName = os.path.splitext(mrcName)[0] + ".png"
        image, header = mrcz.readMRC(mrcName)
        image = util.magickernel( image, k=2 )
        image = ni.gaussian_filter( image, 1.0 )
        
        clim = util.histClim( image, cutoff=1E-4 )
        
        image = util.normalize( np.clip(image, clim[0], clim[1]) )
        
        skimage.io.imsave( pngName, image, plugin='pil' )

                
class Junker(ui_junker.Ui_Junker, QtGui.QApplication):
    
    def __init__(self):
        
        QtGui.QApplication.__init__(self, sys.argv)
        #self.app = QtGui.QApplication(sys.argv)
        self.MainWindow = QtGui.QMainWindow()
        self.setupUi(self.MainWindow)
        
        self.mrcNames = glob.glob( "*.mrc" )
        self.pngNames = [None] * len(self.mrcNames)
        self.baseNames = [None] * len(self.mrcNames)
        self.totalImages = len(self.mrcNames)
        pngNotPresent = np.zeros( len(self.mrcNames), dtype='bool' )
        
        for I, mrcName in enumerate(self.mrcNames):
            self.baseNames[I] = os.path.splitext( mrcName )[0]
            self.pngNames[I] = self.baseNames[I] + ".png"
            pngNotPresent[I] = not os.path.isfile( self.pngNames[I] )
            
        if np.any( pngNotPresent ):
            mrcToDo = np.asarray(self.mrcNames)[pngNotPresent]
            print( "====Processing %d MRC to diagnostic PNG files====" % len(mrcToDo) )
            N_proc = np.minimum( int( mp.cpu_count()/2 ), len(mrcToDo) )
            
            print( mrcToDo )
            
            mrcChunks = cytoolz.partition( N_proc, mrcToDo )
            
            daPool = mp.Pool( N_proc )
            daPool.map_async( batchProcPNG, mrcChunks )
            time.sleep(2.0)
        
        self.eF = keyFilter(self)
        self.installEventFilter( self.eF )
        
        try: os.mkdir( "salvage" )
        except: pass
        try: os.mkdir( "junk" )
        except: pass
    
        self.currIndex = 0
        self.buttonJunk.clicked.connect( self.junkCurrent )
        self.buttonSalvage.clicked.connect( self.salvageCurrent )
        self.buttonUndo.clicked.connect( self.undoCurrent )
        
        try:
            self.labelPNG.setPixmap( QtGui.QPixmap( self.pngNames[self.currIndex] ) )
        except: pass
        

        self.MainWindow.showMaximized()
        self.exec_()
        
    def incrementIndex(self):
        self.currIndex += 1
        if self.currIndex >= len(self.pngNames):
            self.currIndex = 0
        self.updateView()
        
    def decrementIndex(self):
        self.currIndex -= 1
        if self.currIndex < 0:
            self.currIndex = len(self.pngNames) - 1
        self.updateView()
        
    def updateView(self):
        self.statusbar.showMessage( "Image ( %d / %d )" % (self.currIndex, self.totalImages)  )
        if not os.path.isfile( self.pngNames[self.currIndex] ):
            self.labelPNG.setPixmap( QtGui.QPixmap( '' ) )
            return
        
        self.labelPNG.setPixmap( QtGui.QPixmap( self.pngNames[self.currIndex] ) )

    
    def junkCurrent(self):
        junkNames = glob.glob( self.baseNames[self.currIndex] + "*" )
        for junk in junkNames:
            os.rename( junk, os.path.join( "junk", junk ) )
            
        self.updateView()

    
    def salvageCurrent(self):
        salvageNames = glob.glob( self.baseNames[self.currIndex] + "*" )
        for salvage in salvageNames:
            os.rename( salvage, os.path.join( "salvage", salvage ) )
            
        self.updateView()


    def undoCurrent(self):
        undoNames = glob.glob( os.path.join("junk", self.baseNames[self.currIndex] + "*" ) )
        undoNames += glob.glob( os.path.join("salvage", self.baseNames[self.currIndex] + "*" ) )
        for undo in undoNames:
            os.rename( undo, os.path.basename( undo ) )
            
        self.updateView()
    