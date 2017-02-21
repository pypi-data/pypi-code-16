#!/usr/bin/env python
from subprocess import call
from sys import argv
from sys import platform
import re
import os

# Regexs

regex_resize = r'^(\d+)?x(\d+)?'
regex_time   = r'^([\d:]*)(?:$|-([\d:]*)$)'
filenameReg  = r'(.+)(\.\w+)'


noSound   = False
resize    = False
startTime = False
elapse    = False
timed     = False


# Create Command
def runcommand(filename, filenameext, width, height, noSound,resize):
    command = []                                                # Create array
    if platform == 'win32':
        command.append(os.path.join(sys.path[0], 'ffmpeg.exe'))
    else:
        command.append("ffmpeg")                                    # ffmpeg
    if timed:                                                   # Check if timed
        if startTime:
                command.append("-ss")
                command.append(startTime)
        if elapse:
                command.append("-t")
                command.append(elapse)
    command.append("-i")
    command.append(filename + filenameext)                      # File to convert
    command.append("-c:v")                                      # Video Codec
    command.append("libvpx")                                    # Video Codec
    command.append("-crf")                                      # Quality settings
    command.append("32")                                        # Quality settings
    command.append("-b:v")                                      # Quality settings - Bitrate
    command.append("900K")                                      # Quality settings - Bitrate
    command.append("-threads")                                  # Quality settings - Threads
    command.append("1")                                         # Quality settings - Threads
    if noSound:
        command.append("-an")                                   # Disable sound
    else:
        command.append("-c:a")                                  # Audio Codec
        command.append("libvorbis")                             # Audio Codec
    if resize:
        command.append("-vf")                                   # Size
        command.append("scale=" + width + ":" + height)         # Size
    command.append(filename + ".webm")                          # New Filename

    print(command)

    # Call the command

    call(command)



# Info
if len(argv) == 1:
        print("webm.py FILENAME\n-ns -> No audio\n[START FROM]-[DURATION] -> Trims the video duration, use 00:00:00 format or seconds\n[WIDTH]x[HEIGHT] -> Blank keeps aspect ratio - Examples: 640x480 , 640x , x480")

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSlot


app = QApplication(sys.argv)

window = QWidget()

@pyqtSlot()
def filedialog():
    home = os.path.expanduser("~")
    filena = QFileDialog.getOpenFileName(window, 'Open File', home)
    inputfile.setText(filena)

@pyqtSlot()
def gocommand():
    if(mutecheck.isChecked()):
        noSound = True
    else:
        noSound = False
    resize = True
    width = resx.text()
    height = resy.text()
    success = False

    # Get filename
    if re.search(filenameReg, inputfile.text()):
        match = re.search(filenameReg, inputfile.text())

        filename    = match.group(1)
        filenameext = match.group(2)

        gobtn.hide()
        workinglabel.show()

        runcommand(filename, filenameext, width, height, noSound,resize)

        QMessageBox.information(window, "Done", "You can find the webm here\n"+filename+".webm")

        gobtn.show()
        workinglabel.hide()

        success = True

    if success == False:
        QMessageBox.warning(window, "Error", "Input Error")
    success = False


window.setWindowTitle("webmc")

workinglabel = QLabel(window)
workinglabel.setText("Working...\nPlease wait")
workinglabel.move(170,170)
workinglabel.hide()


inputfile = QLineEdit(window)
inputfile.move(10, 20)
inputfile.resize(200,28)

reslabel = QLabel(window)
reslabel.setText("Resolution\n(-1 = Preserve aspect ratio)")
reslabel.move(12,60)

resx = QLineEdit(window)
resx.move(170, 60)
resx.resize(50,25)
resx.setText("-1")

xlabel = QLabel(window)
xlabel.setText("x")
xlabel.move(228,62)

resy = QLineEdit(window)
resy.move(240, 60)
resy.resize(50,25)
resy.setText("-1")

# timefrom = QLineEdit(window)
# timefrom.move(170, 100)
# timefrom.resize(50,25)

# timeto = QLineEdit(window)
# timeto.move(240, 100)
# timeto.resize(50,25)

mutecheck = QCheckBox(window)
mutecheck.move(170, 100)
mutecheck.resize(100,30)
mutecheck.setText("Mute audio")

btn = QPushButton('File...', window)
# btn.setToolTip('Click to quit!')
btn.clicked.connect(filedialog)
btn.resize(btn.sizeHint())
btn.move(220, 20)

gobtn = QPushButton("GO", window)
gobtn.clicked.connect(gocommand)
gobtn.resize(gobtn.sizeHint())
gobtn.move(170,140)



# filename = QFileDialog.getOpenFileName(window, 'Open File', '/')

window.show()


sys.exit(app.exec())


# Parameters
for i in argv:

        # Check if Sound Off

        if i == "-nosound" or i == "-ns":
                soundstring = i
                noSound     = True

        # Check if Resize parameters
        if re.search(regex_resize, i):
                match = re.search(regex_resize, i)

                if match.group(1) is None:
                        width = "-1"
                else:
                        width = match.group(1)

                if match.group(2) is None:
                        height = "-1"
                else:
                        height = match.group(2)
                resize = True

        # Check if Time frame
        if re.search(regex_time, i):
                match = re.search(regex_time, i)

                if match.group(1) is not None:
                        startTime = match.group(1)
                if match.group(2) is not None:
                        elapse = match.group(2)
                timed = True

        # Get filename
        if re.search(filenameReg, i):
                match = re.search(filenameReg, i)

                filename    = match.group(1)
                filenameext = match.group(2)
        runcommand(filename, filenameext, width, height, noSound,resize)
