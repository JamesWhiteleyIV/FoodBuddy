import os
import sys
import random
import string
import datetime
import requests
import json
import pdfkit


class Recipe(object):

    def __init__(self, url, title, tags, notes=None):
        if not url or not title or not tags: 
            raise ValueError("A recipe must have url, title, and at least one tag")

        self.url = url
        self.title = title 
        self.tags = tags
        self.notes = notes


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


    def generateRecipeCode(self):
        """
            Return a random 10 digit code [a-Z0-9].
        """
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]) 


    def getNewRecipePath(self): 
        """
            Returns a non-existing recipe path for new recipe creation.
            Raises OSError if couldn't generate a unique code after 20 retries.
        """
        maxRetries = 20
        code = self.generateRecipeCode()
        recipePath = os.path.join(self.recipesDirectory, code)

        retry = 1 
        while os.path.exists(recipePath) and retry < maxRetries:
            code = self.generateRecipeCode()
            recipePath = os.path.join(self.recipePath, code)
            retry += 1

        if os.path.exists(recipePath):
            raise OSError('Could not generate a unique recipe code.')

        return recipePath


    def urlToPdf(self, url, pdfpath):
        """
            :param url: string 
            :param pdfpath: path to pdf out 
        """
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe") 
        pdfkit.from_url(url, pdfpath, configuration=config)


    def addRecipeFolder(self, recipe):
        """
        """


    def addRecipeMetadata(self, recipe):
        """
        """


    def publishRecipe(self, recipe):
        """
            :param recipe: Recipe object
        """
        addRecipeFolder(recipe)
        addRecipeMetadata(recipe)

        
