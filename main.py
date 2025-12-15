import sys
from PyQt5 import QtWidgets
from gui import AutoKeyGUI
import qt_material


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='dark_purple.xml')
    gui = AutoKeyGUI()
    gui.show()
    sys.exit(app.exec_())