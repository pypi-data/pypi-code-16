'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-02-04

This file is part of Py4Structure.
Py4Structure is a range of free open source structural engineering design 
Python applications.
https://bitbucket.org/lukaszlaba/py4structure/wiki/Home

Py4Structure is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Py4Structure is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOhttp://www.interia.pl/R A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import sys
import subprocess
import os
import codecs

import mistune

from PyQt4 import QtCore, QtGui

from pycore.script_manager import Manager
from pycore.mainwindow_ui import Ui_MainWindow

_appname = 'Py4Structure'
_version = '0.1'

APP_PATH = os.path.dirname(os.path.abspath(__file__))

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #---
        self.ui.pushButton_RunSeePy.clicked.connect(self.pushButton_RunSeePy)
        self.ui.listWidget_ScriptsList.clicked.connect(self.ScriptsListSelectedClicked)
        self.ui.pushButton_RunSelectedScript.clicked.connect(self.pushButton_RunSelectedScript)
        self.ui.comboBox.currentIndexChanged.connect(self.category_changed)
        #---
        self.LoadSeepyList()
        #---
        self.setWindowTitle(_appname + '  ' + _version)
        #---
        self.actionAbout()
        self.ui.actionAbout.triggered.connect(self.actionAbout)
        
    def pushButton_RunSeePy(self):
        subprocess.Popen(['python', '-m', 'seepy.SeePy'])
        
    def LoadSeepyList(self):
        self.ui.comboBox.addItems(script_maneger.categories)
        #--
        allindex = self.ui.comboBox.findText('Any category')
        self.ui.comboBox.setCurrentIndex(allindex)
        
    def ScriptsListSelectedClicked(self):
        scriptname = self.ui.listWidget_ScriptsList.currentItem().text()
        decription = script_maneger.script_description[str(scriptname)]
        text = decription
        self.show_markdown(text)
        
    def pushButton_RunSelectedScript(self):
        scriptname = self.ui.listWidget_ScriptsList.currentItem().text()
        script_maneger.run_some_script(str(scriptname))

    def category_changed(self):
        selected_category = self.ui.comboBox.currentText()
        self.ui.listWidget_ScriptsList.clear()
        self.ui.textBrowser_ScriptDescription.clear()
        scriptlist = script_maneger.get_script_list_for_category(selected_category)
        self.ui.listWidget_ScriptsList.addItems(scriptlist)
    
    def actionAbout(self):
        path = os.path.join(APP_PATH, 'memos/x_about.md')
        markdown = open(path, 'r').read()
        self.show_markdown(markdown)

    def show_markdown(self, markdown):
        code_html = mistune.markdown(markdown)
        self.ui.textBrowser_ScriptDescription.setHtml(codecs.decode(code_html, 'utf-8'))

if __name__ == "__main__":
    #---
    script_maneger = Manager(os.path.join(APP_PATH, 'scripts'))
    #---
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    myapp.show()
    sys.exit(app.exec_())
    