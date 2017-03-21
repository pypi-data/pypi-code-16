import sys
from PyQt5 import QtWidgets
from gui import quotaGUI

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationName('AD Quota Engine')
	form = quotaGUI(sys.argv)
	form.app = app
	form.show()
	sys.exit(app.exec_())