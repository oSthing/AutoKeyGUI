import sys
from PyQt5 import QtWidgets
from gui import AutoKeyGUI


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = AutoKeyGUI()
    gui.show()
    sys.exit(app.exec_())