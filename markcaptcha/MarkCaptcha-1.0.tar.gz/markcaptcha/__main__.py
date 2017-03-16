""" Entry-point for this program"""

import sys

from PyQt5.QtWidgets import QApplication

from markcaptcha.widgets import ConfigWindow

__all__ = ['main']


def main():
    app = QApplication(sys.argv)
    ConfigWindow().show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
