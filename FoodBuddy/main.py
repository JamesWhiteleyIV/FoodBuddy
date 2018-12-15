import os
import sys
import random
import string
import datetime
import requests


class Recipe(object):

    def __init__(self):
        pass


class FoodBuddy(object):

    def __init__(self):
        """
            Validates USERPROFILE variable is set.
            Creates FoodBuddy/recipes directory. 
        """
        self.userProfile = os.environ.get('USERPROFILE', None)
        if not self.userProfile:
            raise EnvironmentError('USERPROFILE environment variable does not exist.') 

        self.directory = os.path.join(self.userProfile, 'FoodBuddy')
        self.recipesDirectory = os.path.join(self.directory, 'recipes')

        if not os.path.exists(self.recipesDirectory):
            os.makedirs(self.recipesDirectory)


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


    def URLtoPDF(self, url, pdfpath):
        """
            :param url: string 
            :param pdfpath: path to pdf out 
        """
        import pdfkit
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe") 
        pdfkit.from_url(url, pdfpath, configuration=config)




    def publishRecipe(self, recipe):
        """
        """
        pass

        
