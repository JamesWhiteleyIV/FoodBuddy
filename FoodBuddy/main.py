import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui  
import api
import traceback
import urllib.request
import re

# TODO: add all this to init of api?
RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.join(RESOURCE_DIR, 'resources')
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DATA_DIR, '..', 'data')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

class ErrorMessage(QtWidgets.QDialog):

    def __init__(self, title, text, copyText=None, icon=None, parent=None):
        super(ErrorMessage, self).__init__(parent)
        self.text = text
        self.copyText = copyText or text
        self._setupUI()
        self._connectSignals()

    def _setupUI(self):
        self.setMinimumWidth(400)
        self.errorTextWidget = QtWidgets.QPlainTextEdit()
        self.errorTextWidget.setPlainText(self.text)

        self.copyButton = QtWidgets.QPushButton("Copy Error")
        self.okayButton = QtWidgets.QPushButton("Ok")
        self.copyButton.setFixedWidth(100)
        self.okayButton.setFixedWidth(100)

        mainLayout = QtWidgets.QGridLayout()
        self.textLayout = QtWidgets.QHBoxLayout()
        self.textLayout.addWidget(self.errorTextWidget)
        self.buttonLayout = QtWidgets.QHBoxLayout()
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
            QtWidgets.QApplication.clipboard().setText(self.copyText)
        self.copyButton.clicked.connect(copyError)
        self.okayButton.clicked.connect(self.accept)


class RecipeListWidget(QtWidgets.QListWidget):
    '''
    List of RecipeItem's
    '''
    def __init__(self, *args, **kwargs):
        super(RecipeListWidget, self).__init__(*args, **kwargs)

    def recipeItemDoubleClicked(self):
        # TODO: use api to open so you don't need to know paths ??
        data = self.currentItem().data
        pdfpath = data.get('pdf', '')
        pdfpath = os.path.join(DATA_DIR, 'recipes', pdfpath)
        notespath = data.get('notes', '')
        notespath = os.path.join(DATA_DIR, 'recipes', notespath)

        if sys.platform.startswith('win'):
            cmd = 'start "" "{}"'.format(pdfpath)
            notescmd  = 'start "" "{}"'.format(notespath)
        elif sys.platform.startswith('darwin'):
            cmd = 'open "{}"'.format(pdfpath)
            notescmd  = 'open "{}"'.format(notespath)
        else:
            raise OSError("This platform is not supported.")

        if pdfpath and os.path.exists(pdfpath):
            os.system(cmd)
        if notespath and os.path.exists(notespath):
            os.system(notescmd)

  
class RecipeItem(QtWidgets.QListWidgetItem):

    def __init__(self, data=None, *args, **kwargs):
        super(RecipeItem, self).__init__(*args, **kwargs)
        self.data = data
        self.setText(data.get('title', ''))


class BrowseWindow(QtWidgets.QDialog):
    """ Used to browse recipes """
    criteriaChange = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(BrowseWindow, self).__init__(*args, **kwargs)
        self.parent = kwargs.get('parent', '') 
        self.setFocus()
        self._setupUI()
        self._connectSignals()

    def _setupUI(self):
        self.setWindowTitle('Recipe Browser')

        if self.parent:
            width = self.parent.geometry().width()
            height = self.parent.geometry().height()
            self.resize(width, height)
        else:
            self.resize(500, 600)

        recipeTagsLabel = QtWidgets.QLabel("Recipe Name/Tags:")
        self.recipeTags = QtWidgets.QLineEdit()
        self.recipeTags.setPlaceholderText("Example: Chicken, tortilla, soup")
        self.clearButton = QtWidgets.QPushButton("Clear")     

        andLabel = QtWidgets.QLabel("Only show recipes that include ALL tags")
        orLabel = QtWidgets.QLabel("Show recipes that include ANY tags")
        self.orButton = QtWidgets.QRadioButton()
        self.andButton = QtWidgets.QRadioButton()
        self.andButton.setChecked(True)

        self.recipeList = RecipeListWidget(self)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.addWidget(andLabel, 0, 0)
        self.mainGridLayout.addWidget(self.andButton, 0, 1)
        self.mainGridLayout.addWidget(orLabel, 1, 0)
        self.mainGridLayout.addWidget(self.orButton, 1, 1)
        self.mainGridLayout.addWidget(recipeTagsLabel, 2, 0)
        self.mainGridLayout.addWidget(self.recipeTags, 2, 1)
        self.mainGridLayout.addWidget(self.clearButton, 2, 2)
        self.mainGridLayout.addWidget(self.recipeList, 3, 0, 1, 3)

        self.mainLayout.addLayout(self.mainGridLayout)
        self.setLayout(self.mainLayout)

    def _connectSignals(self):
        self.clearButton.clicked.connect(self.recipeTags.clear)
        self.recipeTags.textChanged.connect(self.updateRecipes)
        self.andButton.toggled.connect(self.updateRecipes)
        self.recipeList.itemDoubleClicked.connect(self.recipeList.recipeItemDoubleClicked)

    def updateRecipes(self):
        self.criteriaChange.emit()


class StatusLabel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(StatusLabel, self).__init__()
        self.timeoutTimer = QtCore.QTimer(parent=self)
        self.timeoutTimer.setSingleShot(True)

        self.textWidget = QtWidgets.QLabel()
        self.textWidget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.textWidget.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.textWidget.setOpenExternalLinks(True)

        mainLayout = QtWidgets.QHBoxLayout() 
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


class RecipeThumbnailWidget(QtWidgets.QWidget):

    def __init__(self):
        super(RecipeThumbnailWidget, self).__init__()
        self.media = QtWidgets.QLabel()
        self.path = None
        self.setAcceptDrops(True)
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.media)
        self.setLayout(mainLayout)
        self.setDefaultThumb()
        self.x, self.y = 200, 200
        self.media.setMinimumWidth(self.x)
        self.media.setMinimumHeight(self.y)
        self.media.setStyleSheet("QLabel { background-color : rgb(119,136,153); border-radius: 20px;}")

    def setDefaultThumb(self):
        self.media.setText("Drag thumbnail here")
        self.media.setAlignment(QtCore.Qt.AlignCenter)
        self.path = None

    def setImagePreview(self):
        pixmap = QtGui.QPixmap(str(self.path))
        if pixmap is None:
            self.setDefaultThumb()
        else:
            w = self.media.width()
            h = self.media.height()
            pixmap = pixmap.scaled(w, h, QtCore.Qt.KeepAspectRatio)
            self.media.setPixmap(pixmap)

    def saveThumbToTemp(self, path):
        name, ext = os.path.splitext(path)
        self.path = os.path.join(TEMP_DIR, 'temp'+ext)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(path, self.path)

    def setThumbnail(self, path):
        if re.match('.*\.(jpg|psd|png|gif|tga|tif|bmp)$', path):
            self.saveThumbToTemp(path)
            self.setImagePreview()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            url = e.mimeData().urls()[0]
            path = os.path.join(url.toString())
            self.setThumbnail(path)
        else:
            e.ignore()



class FoodBuddyWidget(QtWidgets.QWidget):

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

        recipeThumbLabel = QtWidgets.QLabel("Recipe Thumbnail:")
        self.recipeThumb = RecipeThumbnailWidget()
        self.clearButton1 = QtWidgets.QPushButton("Clear")     

        recipeTitleLabel = QtWidgets.QLabel("Recipe Title:")
        self.recipeTitle = QtWidgets.QLineEdit()
        self.recipeTitle.setPlaceholderText("Example: Chicken Soup")
        self.clearButton2 = QtWidgets.QPushButton("Clear")     

        recipeTagsLabel = QtWidgets.QLabel("Recipe Tags:")
        self.recipeTags = QtWidgets.QLineEdit()
        self.recipeTags.setPlaceholderText("Example: Chicken, tortilla, soup")
        self.clearButton3 = QtWidgets.QPushButton("Clear")     

        recipeNotesLabel = QtWidgets.QLabel("Recipe Notes:")
        self.recipeNotes = QtWidgets.QTextEdit()
        self.recipeNotes.setMinimumHeight(200)
        recipeNotesLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

        self.browseButton = QtWidgets.QPushButton("Browse Recipes")     
        self.browseButton.setMaximumWidth(100)
        self.addButton = QtWidgets.QPushButton("Add Recipe")     
        self.addButton.setMaximumWidth(100)
        self.addButton.setEnabled(False)

        self.statusLabel = StatusLabel()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.browseButton)
        self.buttonLayout.addWidget(self.addButton)

        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.addWidget(recipeThumbLabel, 0, 0)
        self.mainGridLayout.addWidget(self.recipeThumb, 0, 1)
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
        self.clearButton1.clicked.connect(self.recipeThumb.setDefaultThumb)
        self.clearButton2.clicked.connect(self.recipeTitle.clear)
        self.clearButton3.clicked.connect(self.recipeTags.clear)
        #self.recipeUrl.textChanged.connect(self.updateAddButton)
        self.recipeTitle.textChanged.connect(self.updateAddButton)
        self.recipeTags.textChanged.connect(self.updateAddButton)
        self.addButton.clicked.connect(self.addRecipe)
        self.browseButton.clicked.connect(self.openRecipeBrowser)

    def center(self):
        """ Centers GUI in middle of screen """
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def updateStatus(self, message, **kwargs):
        kwargs['styling'] = 'color: white; background: grey; padding: 3px;' + kwargs.get('styling', '')
        self.statusLabel.showMessage(message, **kwargs)
        self.repaint()
        QtCore.QCoreApplication.processEvents()

    def updateAddButton(self):
        '''
        if self.recipeUrl.text() == '':
            self.addButton.setEnabled(False)
        '''
        if self.recipeTitle.text() == '':
            self.addButton.setEnabled(False)
        elif self.recipeTags.text() == '':
            self.addButton.setEnabled(False)
        else:
            self.addButton.setEnabled(True)

    def generateRecipe(self): 
        #url = str(self.recipeUrl.text())
        url = 'test'
        title = str(self.recipeTitle.text())
        notes = str(self.recipeNotes.toPlainText())
        tags = str(self.recipeTags.text())
        tags = [x.strip() for x in tags.split(',')]
        recipe = api.Recipe(url, title, tags, notes)
        return recipe

    def openRecipeBrowser(self):
        if self.recipeBrowser is None:
            self.recipeBrowser = BrowseWindow(parent=self) 
            self.recipeBrowser.criteriaChange.connect(self.setBrowserRecipes)
        self.recipeBrowser.updateRecipes()
        self.recipeBrowser.show()
        self.recipeBrowser.raise_()

    def setBrowserRecipes(self):
        if self.recipeBrowser:
            tags = str(self.recipeBrowser.recipeTags.text())
            tags = [x.strip() for x in tags.split(',')]

            if self.recipeBrowser.andButton.isChecked():
                searchBy = 'AND'
            else:
                searchBy = 'OR'
            recipes = self.foodBuddy.getRecipesByTags(tags, searchBy)

            self.recipeBrowser.recipeList.clear()
            for code, data in recipes.items():
                recipeItem = RecipeItem(data) 
                self.recipeBrowser.recipeList.addItem(recipeItem)
            self.recipeBrowser.recipeList.sortItems()


    def addRecipe(self):
        try:
            self.updateStatus("Adding Recipe, this may take a minute...")
            self.addButton.setEnabled(False)
            recipe = self.generateRecipe()
            self.foodBuddy.createRecipe(recipe)
        except Exception as err:
            self.updateStatus(
                    "Error adding recipe",
                    styling='background: red;')
            stacktrace = traceback.format_exc()
            message = ErrorMessage(
                        "Error",
                        "The following error occurred:\n{}".format(stacktrace),
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
    app = QtWidgets.QApplication(sys.argv)
    GUI = FoodBuddyWidget()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()


