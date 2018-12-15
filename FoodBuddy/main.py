import os
import sys

class FoodBuddy(object):

    def __init__(self):
        self.userProfile = os.environ.get('USERPROFILE', None)
        self.createRecipesPath()


    def createRecipesPath(self):
        if not self.userProfile:
            raise EnvironmentError('User profile environment variable does not exist.') 

        self.recipesPath = os.path.join(self.userProfile, 'FoodBuddy', 'recipes')
        if not os.path.exists(self.recipesPath):
            os.makedirs(self.recipesPath)
            print 'making dirs...', self.recipesPath
            

    def generateRecipeCode(self):
        """
            Creates a random 10 digit code [a-Z0-9].
            Checks if self.recipesPath / code exists, if so keeps trying to generate code up to 20 retries.
            if not, creates directory.
        """
        maxRetries = 20

        

