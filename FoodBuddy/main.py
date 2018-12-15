import os
import sys

class FoodBuddy(object):

    def __init__(self):
        userProfile = os.environ.get('USERPROFILE', None)
        if not userProfile:
            raise EnvironmentError('User profile environment variable does not exist.') 

        self.recipesPath = os.path.join(userProfile, 'FoodBuddy', 'recipes')
        if not os.path.exists(self.recipesPath):
            os.makedirs(self.recipesPath)
            print 'making dirs...'
            


        

