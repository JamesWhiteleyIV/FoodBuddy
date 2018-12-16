import os
import sys
from PyQt4 import QtCore, QtGui, QtWidgets


dialogs = {}


class QInstanceManager(object):
    def __init__(self, *args):
        super(QInstanceManager, self).__init__()
        self.hadInstance = False

    def __enter__(self):
        qapp = QtWidgets.QApplication.instance()
        self.hadInstance = bool(qapp)
        if not self.hadInstance:
            QtWidgets.QApplication(sys.argv)

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.hadInstance:
            qapp = QtWidgets.QApplication.instance()
            sys.exit(qapp.exec_())


class FoodBuddyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FoodBuddyDialog, self).__init__(parent)
        try:
            self.setupUI()
        except Exception as err:
            import traceback
            traceback.print_exc()

    def setupUI(self):
        logo = os.path.join(RESOURCE_DIR, "foodbuddy.jpg")

        font = QtGui.QFont("AnyStyle", 12)
        pixmap = QtGui.QPixmap(logo)
        splash = QtWidgets.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
        splash.setFont(font)
        splash.show()

		self.setLayout(mainLayout)
        self.setStyleSheet(self.getStyle())
        self.setWindowTitle("Food Buddy")

    def getStyle(self):
        pass


def launch():
    global dialogs
    with QInstanceManager():
        dialog = dialogs['foodbuddy'] = FoodBuddyDialog()
        dialog.raise_()
        dialog.show()
    return dialog


if __name__ == '__main__':
    launch()
