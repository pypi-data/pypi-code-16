import sys
from PyQt5 import QtWidgets
from .gui import quotaGUI

def run():
	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationName('AD Quota Engine')
	form = quotaGUI(sys.argv)
	form.app = app
	form.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	run()