#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os

from PyQt5.QtWidgets import (QWidget, QComboBox, QApplication, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap

from configparser import ConfigParser
from easy_languages.locale import locale


class GUI(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):


        getlocale = locale()
        langs = getlocale.returnlocales()
        self.combo = QComboBox(self)

        if len(langs) != 0:
            self.combo.addItems(langs)
        else:
            raise Exception('Locales not found')



        self.combo.move(25, 25)
        self.combo.setFixedSize(200, 50)

        btn = QPushButton(self)
        self.setWindowIcon(QIcon(QPixmap(__file__.split("/")[:len(__file__.split("/"))-1] + "icos/langchoosing.png")))
        btn.move(250, 25)
        btn.setText('Set')
        btn.setFixedSize(125, 50)
        #btn.clicked.connect(self.buttonClicked)


        btn.clicked.connect(self.choose)


        self.setFixedSize(400, 100)
        self.setWindowTitle('Choose language')
        self.show()

    def choose(self):
        lang = self.combo.currentText()
        parser = ConfigParser()
        if 'config.ini' not in os.listdir('locales'): raise Exception('config.ini does not exist')

        parser.read('locales/config.ini')
        parser['main']['language'] = lang

        with open('locales/config.ini', 'w') as configfile:  # save
            parser.write(configfile)
        self.close()




def show():
    app = QApplication(sys.argv)
    ex = GUI()
    app.exec()

def debug():
    print(__file__)

