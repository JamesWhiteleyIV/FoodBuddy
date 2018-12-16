import sys
from PyQt4 import QtGui 

def MainWidget():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    window.setGeometry(0, 0, 500, 300)
    window.show()

    sys.exit(app.exec_())



if __name__ == "__main__":
    MainWidget()


