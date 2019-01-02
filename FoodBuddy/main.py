import sys
import os
from PyQt4 import QtGui, QtCore
import api


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



class RecipeListWidget(QtGui.QWidget):

    def __init__(self, *args, **kwargs):
        super(RecipeListWidget, self).__init__(*args, **kwargs)
        self._setupUI()

    def _setupUI(self):
        mainLayout = QtCore.QVBoxLayout()
        self.setLayout(mainLayout)

    def addRecipeWidget(self, widget):
        pass

    def clearRecipeWidgets(self):
        pass


class RecipeWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(RecipeWidget, self).__init__(*args, **kwargs)
        self.data = data
        self._setupUI()

    def _setupUI(self):
        self.title = self.data.get('title', '')

        mainLayout = QtCore.QHBoxLayout()
        mainLayout.addWidget()
        self.setLayout(mainLayout)



class BrowseWindow(QtGui.QDialog):
    """ Used to browse recipes """
    criteriaChange = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(BrowseWindow, self).__init__(*args, **kwargs)
        self.setFocus()
        self._setupUI()
        self._connectSignals()

    def _setupUI(self):
        self.setWindowTitle('Recipe Browser')

        recipeTagsLabel = QtGui.QLabel("Recipe Tags:")
        self.recipeTags = QtGui.QLineEdit()
        self.recipeTags.setPlaceholderText("Example: Chicken, tortilla, soup")
        self.clearButton = QtGui.QPushButton("Clear")     

        andLabel = QtGui.QLabel("Only show recipes that include ALL tags")
        orLabel = QtGui.QLabel("Show recipes that include ANY tags")
        self.orButton = QtGui.QRadioButton()
        self.andButton = QtGui.QRadioButton()
        self.andButton.setChecked(True)

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainGridLayout = QtGui.QGridLayout()
        self.mainGridLayout.addWidget(andLabel, 0, 0)
        self.mainGridLayout.addWidget(self.andButton, 0, 1)
        self.mainGridLayout.addWidget(orLabel, 1, 0)
        self.mainGridLayout.addWidget(self.orButton, 1, 1)
        self.mainGridLayout.addWidget(recipeTagsLabel, 2, 0)
        self.mainGridLayout.addWidget(self.recipeTags, 2, 1)
        self.mainGridLayout.addWidget(self.clearButton, 2, 2)

        self.mainLayout.addLayout(self.mainGridLayout)
        self.setLayout(self.mainLayout)

    def _connectSignals(self):
        self.clearButton.clicked.connect(self.recipeTags.clear)
        self.recipeTags.textChanged.connect(self.updateRecipes)
        self.andButton.toggled.connect(self.updateRecipes)

    def updateRecipes(self):
        self.criteriaChange.emit()


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

    def showMessage(self, message, timeout=None, styling=''):
        self.textWidget.setText(message)
        self.textWidget.setStyleSheet(styling)
        self.show()
        if timeout:
            self.timeoutTimer.start(timeout)


# TODO: make it so you can drag in word, txt, pdf file
class RecipeUrlWidget(QtGui.QLineEdit):

    def __init__(self):
        super(RecipeUrlWidget, self).__init__()
        self.setDragEnabled(True)
        self.setPlaceholderText("Drag or type URL  Example: https://www.allrecipes.com/recipe/257938")

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
        self.recipeBrowser = None
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

        recipeUrlLabel = QtGui.QLabel("Recipe URL:")
        self.recipeUrl = RecipeUrlWidget()
        self.clearButton1 = QtGui.QPushButton("Clear")     

        recipeTitleLabel = QtGui.QLabel("Recipe Title:")
        self.recipeTitle = QtGui.QLineEdit()
        self.recipeTitle.setPlaceholderText("Example: Chicken Soup")
        self.clearButton2 = QtGui.QPushButton("Clear")     

        recipeTagsLabel = QtGui.QLabel("Recipe Tags:")
        self.recipeTags = QtGui.QLineEdit()
        self.recipeTags.setPlaceholderText("Example: Chicken, tortilla, soup")
        self.clearButton3 = QtGui.QPushButton("Clear")     

        recipeNotesLabel = QtGui.QLabel("Recipe Notes:")
        self.recipeNotes = QtGui.QTextEdit()
        self.recipeNotes.setMinimumHeight(200)
        recipeNotesLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        self.browseButton = QtGui.QPushButton("Browse Recipes")     
        self.browseButton.setMaximumWidth(100)
        self.addButton = QtGui.QPushButton("Add Recipe")     
        self.addButton.setMaximumWidth(100)
        self.addButton.setEnabled(False)

        self.statusLabel = StatusLabel()
        self.mainLayout = QtGui.QVBoxLayout()
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.browseButton)
        self.buttonLayout.addWidget(self.addButton)

        self.mainGridLayout = QtGui.QGridLayout()
        self.mainGridLayout.addWidget(recipeUrlLabel, 0, 0)
        self.mainGridLayout.addWidget(self.recipeUrl, 0, 1)
        self.mainGridLayout.addWidget(self.clearButton1, 0, 2)
        self.mainGridLayout.addWidget(recipeTitleLabel, 1, 0)
        self.mainGridLayout.addWidget(self.recipeTitle, 1, 1)
        self.mainGridLayout.addWidget(self.clearButton2, 1, 2)
        self.mainGridLayout.addWidget(recipeTagsLabel, 2, 0)
        self.mainGridLayout.addWidget(self.recipeTags, 2, 1)
        self.mainGridLayout.addWidget(self.clearButton3, 2, 2)
        self.mainGridLayout.addWidget(recipeNotesLabel, 3, 0, 1, 1)
        self.mainGridLayout.addWidget(self.recipeNotes, 3, 1, 1, 2)
        self.mainGridLayout.addLayout(self.buttonLayout, 4, 0, 1, 3)
        self.mainGridLayout.addWidget(self.statusLabel, 5, 0, 1, 3)

        self.mainLayout.addLayout(self.mainGridLayout)
        self.setLayout(self.mainLayout)

    def _connectSignals(self):
        self.clearButton1.clicked.connect(self.recipeUrl.clear)
        self.clearButton2.clicked.connect(self.recipeTitle.clear)
        self.clearButton3.clicked.connect(self.recipeTags.clear)
        self.recipeUrl.textChanged.connect(self.updateAddButton)
        self.recipeTitle.textChanged.connect(self.updateAddButton)
        self.recipeTags.textChanged.connect(self.updateAddButton)
        self.addButton.clicked.connect(self.addRecipe)
        self.browseButton.clicked.connect(self.openRecipeBrowser)

    def center(self):
        """ Centers GUI in middle of screen """
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def updateStatus(self, message, **kwargs):
        kwargs['styling'] = 'color: white; background: grey; padding: 3px;' + kwargs.get('styling', '')
        self.statusLabel.showMessage(message, **kwargs)
        self.repaint()
        QtCore.QCoreApplication.processEvents()

    def updateAddButton(self):
        if self.recipeUrl.text() == '':
            self.addButton.setEnabled(False)
        elif self.recipeTitle.text() == '':
            self.addButton.setEnabled(False)
        elif self.recipeTags.text() == '':
            self.addButton.setEnabled(False)
        else:
            self.addButton.setEnabled(True)

    def generateRecipe(self): 
        url = str(self.recipeUrl.text())
        title = str(self.recipeTitle.text())
        notes = str(self.recipeNotes.toPlainText())
        tags = str(self.recipeTags.text())
        tags = [x.strip() for x in tags.split(',')]
        recipe = api.Recipe(url, title, tags, notes)
        return recipe

    def openRecipeBrowser(self):
        if self.recipeBrowser is None:
            self.recipeBrowser = BrowseWindow(self) 
            self.recipeBrowser.criteriaChange.connect(self.setBrowserRecipes)
        self.recipeBrowser.show()
        self.recipeBrowser.raise_()

    def setBrowserRecipes(self):
        if self.recipeBrowser:
            tags = str(self.recipeBrowser.recipeTags.text())
            tags = [x.strip() for x in tags.split(',')]
            if self.recipeBrowser.andButton.isChecked():
                searchBy = 'AND'
                print "AND"
            else:
                searchBy = 'OR'
                print "OR"
            recipes = self.foodBuddy.getRecipesByTags(tags, searchBy)
            for key, value in recipes.iteritems():
                print key, '-->', value


    def addRecipe(self):
        try:
            self.updateStatus("Adding Recipe, this may take a minute...")
            self.addButton.setEnabled(False)
            recipe = self.generateRecipe()
            self.foodBuddy.publishRecipe(recipe)
        except Exception as err:
            self.updateStatus(
                    "Error adding recipe",
                    styling='background: red;')
            message = ErrorMessage(
                        "Error",
                        "The following error occurred: {}".format(err),
                        parent=self)
            message.exec_()
            self.addButton.setEnabled(True)
            return
        else:
            self.updateStatus(
                    "Recipe added successfully",
                    styling='background: green;')
            self.addButton.setEnabled(True)

def run():
    app = QtGui.QApplication(sys.argv)
    GUI = FoodBuddyWidget()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()


