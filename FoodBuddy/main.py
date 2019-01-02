import sys
import os
from PyQt4 import QtGui, QtCore
import api

"""
#recipe = api.Recipe('url', 'title', ['chicken', 'taco'], 'notesss')

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


class BrowseWindow(QtGui.QDialog):
    """ Used to browse recipes """
    def __init__(self, *args, **kwargs):
        super(BrowseWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('Recipe Browser')

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)


class StatusLabel(QtGui.QWidget):
    def __init__(self, parent=None):
        super(StatusLabel, self).__init__()
        self.timeoutTimer = QtCore.QTimer(parent=self)
        self.timeoutTimer.setSingleShot(True)

        self.textWidget = QtGui.QLabel()
        self.textWidget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.textWidget.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.textWidget.setOpenExternalLinks(True)

        mainLayout = QtGui.QHBoxLayout() 
        mainLayout.addWidget(self.textWidget)
        self.setLayout(mainLayout)

        self.timeoutTimer.timeout.connect(self._onTimeout)
        self.hide()

    def _onTimeout(self):
        self.textWidget.setText('')
        self.textWidget.setToolTip('')
        self.textWidget.setStyleSheet('')
        self.hide()

    def showMessage(self, message, timeout=None):
        self.textWidget.setText(message)
        self.show()
        if timeout:
            self.timeoutTimer.start(timeout)


class RecipeUrlWidget(QtGui.QLineEdit):

    def __init__(self):
        super(RecipeUrlWidget, self).__init__()
        self.setDragEnabled(True)
        self.setPlaceholderText("Drag or type URL of recipe here")

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() in ('http', 'https'):
            filepath = urls[0].toString() 
            self.setText(filepath)


class FoodBuddyWidget(QtGui.QWidget):

    def __init__(self):
        super(FoodBuddyWidget, self).__init__()
        self.foodBuddy = api.FoodBuddy()
        self._setupUI()
        self._connectSignals()
        self.setFocus()
        self.show()

    def _setupUI(self):
        self.setGeometry(50, 50, 600, 800)
        self.setWindowTitle("FoodBuddy")
        burgerIcon = os.path.join(RESOURCE_DIR, 'burger.png')
        self.setWindowIcon(QtGui.QIcon(burgerIcon))
        self.center()

        self.recipeUrl = RecipeUrlWidget()
        print self.recipeUrl.placeholderText()
        self.clearButton = QtGui.QPushButton("Clear")     
        """
        self.recipeTitle
        self.recipeNotes
        self.recipeTags
        self.browseButton
        self.AddButton
        """
        self.statusLabel = StatusLabel()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainGridLayout = QtGui.QGridLayout()
        self.mainGridLayout.addWidget(self.recipeUrl, 0, 0)
        self.mainGridLayout.addWidget(self.clearButton, 0, 1)
        self.mainGridLayout.addWidget(self.statusLabel, 1, 0)

        self.mainLayout.addLayout(self.mainGridLayout)
        self.setLayout(self.mainLayout)

    def _connectSignals(self):
        self.clearButton.clicked.connect(self.recipeUrl.clear)

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


