import sys
import os
from PyQt4 import QtGui, QtCore
import api

"""
NOTE: sample error
message = ErrorMessage(
            "User Error",
            "Could not create pdf of recipe",
            parent=self)
        message.exec_()
        return

"""

RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(RESOURCE_DIR, 'resources')

class ErrorMessage(QtGui.QDialog):

    def __init__(self, title, text, copyText=None, icon=None, parent=None):
        super(ErrorMessage, self).__init__(parent)
        self.text = text
        self.copyText = copyText or text
        self._setupUI()
        self._connectSignals()

    def _setupUI(self):
        self.setMinimumWidth(400)
        self.errorTextWidget = QtGui.QPlainTextEdit()
        self.errorTextWidget.setPlainText(self.text)

        self.copyButton = QtGui.QPushButton("Copy Error")
        self.copyButton.setFixedWidth(100)
        self.okayButton = QtGui.QPushButton("Ok")
        self.okayButton.setFixedWidth(100)

        mainLayout = QtGui.QGridLayout()
        self.textLayout = QtGui.QHBoxLayout()
        self.textLayout.addWidget(self.errorTextWidget)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.addStretch(0)
        self.buttonLayout.addWidget(self.copyButton)
        self.buttonLayout.addWidget(self.okayButton)
        mainLayout.addLayout(self.textLayout, 0, 0)
        mainLayout.addLayout(self.buttonLayout, 1, 0)

        self.setWindowTitle("ERROR")

        self.setLayout(mainLayout)
        self.okayButton.setFocus()

    def _connectSignals(self):
        def copyError():
            QtGui.QApplication.clipboard().setText(self.copyText)
        self.copyButton.clicked.connect(copyError)
        self.okayButton.clicked.connect(self.accept)


class FoodBuddyWidget(QtGui.QWidget):

    def __init__(self):
        super(FoodBuddyWidget, self).__init__()
        self._setupUI()
        self.show()

    def _setupUI(self):
        self.setGeometry(50, 50, 600, 800)
        self.setWindowTitle("FoodBuddy")
        burgerIcon = os.path.join(RESOURCE_DIR, 'burger.png')
        self.setWindowIcon(QtGui.QIcon(burgerIcon))
        self.center()

    def _connectSignals(self):
        pass

    def center(self):
        """ Centers GUI in middle of screen """
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

def run():
    app = QtGui.QApplication(sys.argv)
    GUI = FoodBuddyWidget()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()


