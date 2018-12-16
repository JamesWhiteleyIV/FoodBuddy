import os
import sys
import random
import string
import datetime
import requests
import json
import pdfkit


class Recipe(object):

    def __init__(self, url, title, tags, notes="", thumbnail=None):
        """
            :param url: <str>
            :param title: <str>
            :param tags: list of <str> 
            :param notes: <str> 
            :param thumbnail: <str> path to thumbnail image
        """
        self.url = url
        self.title = title 
        self.tags = tags
        self.notes = notes
        self.thumbnail = thumbnail
        self._validate()

    def _validate(self):
        if not self.url or not self.title or not self.tags: 
            raise ValueError("A recipe must have url, title, and at least one tag")

        if not isinstance(self.tags, list):
            raise ValueError("A recipe must have url, title, and at least one tag")
    
        if len(self.tags) < 1:
            raise ValueError("A recipe must have url, title, and at least one tag")


class FoodBuddy(object):

    def __init__(self):
        """
            Validates USERPROFILE variable is set.
            Creates FoodBuddy/recipes directory. 
            Creates FoodBuddy/metadata.json file.
        """
        self.userProfile = os.environ.get('USERPROFILE', None)
        self.directory = os.path.join(self.userProfile, 'FoodBuddy')
        self.recipesDirectory = os.path.join(self.directory, 'recipes')
        self.metadataDirectory = os.path.join(self.directory, 'metadata.json') 

        if not self.userProfile:
            raise EnvironmentError('USERPROFILE environment variable does not exist.') 

        if not os.path.exists(self.recipesDirectory):
            os.makedirs(self.recipesDirectory)

        if not os.path.exists(self.metadataDirectory):
            with open(self.metadataDirectory, 'w') as fp:
                data = {"recipes": {}}
                json.dump(data, fp, indent=4)


    def _generateRecipeCode(self):
        """
            Return a random 10 digit code [a-Z0-9].
        """
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]) 


    def _getNewRecipePath(self): 
        """
            Returns a non-existing recipe path for new recipe creation.
            Raises OSError if couldn't generate a unique code after 20 retries.
        """
        maxRetries = 20
        code = self._generateRecipeCode()
        recipePath = os.path.join(self.recipesDirectory, code)

        retry = 1 
        while os.path.exists(recipePath) and retry < maxRetries:
            code = self._generateRecipeCode()
            recipePath = os.path.join(self.recipePath, code)
            retry += 1

        if os.path.exists(recipePath):
            raise OSError('Could not generate a unique recipe code.')

        return recipePath


    def _urlToPdf(self, url, pdfpath):
        """
            :param url: string 
            :param pdfpath: path to pdf out 
        """
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe") 
        pdfkit.from_url(url, pdfpath, configuration=config)


    def _addRecipeFolder(self, recipe):
        """
            :param recipe: Recipe object

            Creates FoodBuddy/recipes/<code> directory. 
            Create pdf from URL in directory.
            Create txt file from notes in directory.
        """
        recipePath = self._getNewRecipePath()
        os.makedirs(recipePath)

        pdfPath = os.path.join(recipePath, 'recipe.pdf')
        self._urlToPdf(recipe.url, pdfPath)

        notesPath = os.path.join(recipePath, 'notes.txt')
        with open(notesPath, 'w') as fp:
            fp.write(recipe.notes)

        # TODO: setup thumbnail support
        #if recipe.thumbnail:
        #     copy from added path --> <recipe code>/thumbnail.<ext>


    def _addRecipeMetadata(self, recipe):
        """
            :param recipe: Recipe object

            Adds:
            <code> : {
                'title': <title>,
                'tags': [<tag1>, <tag2>, ... ],
                'pdf': <path to pdf>,
                'notes': <path to notes>,
                'thumbnail': <path to thumbnail>
            }
        """
        with open(self.metadataDirectory, 'r') as fp:
            data = json.load(fp)

        print "ADD RECIPE TO META DATA"
        print data


    def publishRecipe(self, recipe):
        """
            :param recipe: Recipe object

            Creates recipe on disk.
            Adds recipe to metadata.json.
        """
        self._addRecipeFolder(recipe)
        self._addRecipeMetadata(recipe)

        
