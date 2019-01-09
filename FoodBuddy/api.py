import os
import sys
import random
import string
import datetime
import json
import pathlib
import shutil

DATA_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
DATA_DIR = os.path.join(DATA_DIR, '..', 'data')
RECIPES_DIR = os.path.join(DATA_DIR, 'recipes')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')
LOG_FILE = os.path.join(DATA_DIR, 'log.txt')
METADATA_FILE = os.path.join(DATA_DIR, 'metadata.json')
#sys.stdout = open(LOG_FILE, "w")

class Recipe(object):

    def __init__(self, thumbnail, title, tags, notes=""):
        """
            :param thumbnail: <str> path to thumbnail
            :param title: <str>
            :param tags: list of <str> 
            :param notes: <str> 
            :param thumbnail: <str> path to thumbnail image
        """
        self.id = self._generateRecipeID()
        self.thumbnail = pathlib.Path(str(thumbnail)) if thumbnail else None
        self.title = title 
        self.tags = tags
        self.notes = notes
        self._validate()

    def _validate(self):
        if not isinstance(self.tags, list):
            raise ValueError("A recipe must have a title, and at least one tag")
    
        if len(self.tags) < 1:
            raise ValueError("A recipe must have a title, and at least one tag")

    def _generateRecipeID(self):
        """
        Returns next highest available number in recipes dir.
        """
        recipes = [int(x) for x in os.listdir(RECIPES_DIR)]
        if not recipes:
            return '1' 

        return str(max(recipes) + 1)


class FoodBuddy(object):

    def __init__(self):
        """
            Creates FoodBuddy/data directory. 
            Creates FoodBuddy/data/temp directory. 
            Creates FoodBuddy/data/recipes directory. 
            Creates FoodBuddy/data/metadata.json file.
            Creates FoodBuddy/data/log.txt file.
        """
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        if not os.path.exists(RECIPES_DIR):
            os.makedirs(RECIPES_DIR)

        if not os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'w') as fp:
                data = {"recipes": {}}
                json.dump(data, fp, indent=4)

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as fp:
                fp.write('')
 

    def _addRecipeFolder(self, recipe):
        """
            :param recipe: Recipe object

            Creates FoodBuddy/recipes/<ID> directory. 
            Create pdf from URL in directory.
            Create txt file from notes in directory.
        """
        recipePath = os.path.join(RECIPES_DIR, recipe.id) 

        if os.path.exists(recipePath):
            raise OSError("Conflicting ID for recipe.")

        os.makedirs(recipePath)

        if recipe.thumbnail:
            thumbPath = os.path.join(recipePath, recipe.thumbnail.name)
            shutil.copy2(str(recipe.thumbnail), thumbPath)

        notesPath = os.path.join(recipePath, 'notes.txt')
        with open(notesPath, 'w') as fp:
            fp.write(recipe.notes)


    def _loadMetadata(self):
        """
            Loads metadata.json into dictionary and returns it.
            Raises IOError if something went wrong loading the file.
        """
        with open(METADATA_FILE, 'r') as fp:
            data = json.load(fp)
        
        if not data:
            raise IOError('Could not open metadata.json')

        return data
    

    def _addRecipeMetadata(self, recipe):
        """
            :param recipe: Recipe object

            Adds:
            <ID> : {
                'title': <title>,
                'tags': [<tag1>, <tag2>, ... ],
                'thumb': <path to thumb>,
                'notes': <path to notes>,
                'created': <datetime fo creation>,
            }
        """
        thumbPath = os.path.join(recipe.id, recipe.thumbnail.name) if recipe.thumbnail else None
        notesPath = os.path.join(recipe.id, 'notes.txt')

        data = self._loadMetadata()
        if recipe.id in data['recipes']:
            raise KeyError("This recipe ID already exists in metadata.json.")

        data['recipes'][recipe.id] = {
                'id': recipe.id,
                'title': recipe.title,
                'tags': recipe.tags,
                'notes': notesPath, 
                'thumb': thumbPath, 
                'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

        with open(METADATA_FILE, 'w') as fp:
            json.dump(data, fp, indent=4)


    def createRecipe(self, recipe):
        """
            :param recipe: Recipe object

            Creates recipe on disk.
            Adds recipe to metadata.json.
        """
        self._addRecipeFolder(recipe)
        self._addRecipeMetadata(recipe)

    # TODO:
    def updateRecipe(self):
        pass

    def deleteRecipe(self, recipeID):
        """
        Removes recipe from metadata.json. 
        Deletes recipe folder.

        Returns True on success, else False.
        """
        data = self._loadMetadata()
        data['recipes'].pop(recipeID, None)

        with open(METADATA_FILE, 'w') as fp:
            json.dump(data, fp, indent=4)

        for id_ in os.listdir(RECIPES_DIR):
            if id_ == recipeID:
                path = os.path.join(RECIPES_DIR, id_)
                shutil.rmtree(path)
                return True
        
        return False


    def getRecipesByTags(self, tags, searchBy='AND'):
        """
            :param tags: list of <str>
            :param searchBy: <str> of either 'AND' or 'OR', which will be used to check tags. 

            Looks in metadata.json and compares tags, AND will match recipes including all tags.
            OR will match a recipe if it contains any of the tags in the tags list.
        """
        matches = {}
        tags = [x.lower() for x in tags if x != ''] # force lowercase

        data = self._loadMetadata()
        allrecipes = data.get('recipes', {})

        if tags == []:
            return allrecipes

        for key, recipe in allrecipes.items():
            title = recipe.get('title', '')
            titlesplit = title.split()
            metatags = recipe.get('tags', [])
            metatags = [x.lower() for x in metatags]
            metatags += titlesplit

            if searchBy == 'AND':
                if set(tags).issubset(set(metatags)): 
                    matches[key] = recipe
            elif searchBy == 'OR':
                if any(t in tags for t in metatags):
                    matches[key] = recipe

        return matches





