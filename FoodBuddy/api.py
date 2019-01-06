import os
import sys
import random
import string
import datetime
import json
import pdfkit

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DATA_DIR, '..', 'data')
LOG_FILE = os.path.join(DATA_DIR, 'log.txt')
sys.stdout = open(LOG_FILE, "w")

class Recipe(object):

    def __init__(self, url, title, tags, notes="", thumbnail=None):
        """
            :param url: <str>
            :param title: <str>
            :param tags: list of <str> 
            :param notes: <str> 
            :param thumbnail: <str> path to thumbnail image
        """
        self.id = self._generateRecipeID()
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

    def _generateRecipeID(self):
        """
            Return a random 10 digit string [a-Z0-9].
        """
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]) 

    def generateNewID(self):
        self.id = self._generateRecipeID()


class FoodBuddy(object):

    def __init__(self):
        """
            Validates USERPROFILE variable is set.
            Creates FoodBuddy/data/recipes directory. 
            Creates FoodBuddy/data/metadata.json file.
        """
        self.recipesDirectory = os.path.join(DATA_DIR, 'recipes')
        self.metadataDirectory = os.path.join(DATA_DIR, 'metadata.json') 

        if not os.path.exists(self.recipesDirectory):
            os.makedirs(self.recipesDirectory)

        if not os.path.exists(self.metadataDirectory):
            with open(self.metadataDirectory, 'w') as fp:
                data = {"recipes": {}}
                json.dump(data, fp, indent=4)


    def _urlToPdf(self, url, pdfpath):
        """
            :param url: string 
            :param pdfpath: path to pdf out 
        """
        if sys.platform.startswith('win'):
            path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" 
        elif sys.platform.startswith('darwin'):
            path = r"/usr/local/bin/wkhtmltopdf"
        else:
            raise OSError("Could not locate USERPROFILE or HOME environment variable")

        config = pdfkit.configuration(wkhtmltopdf=path)
        pdfkit.from_url(url, pdfpath, configuration=config)


    def _addRecipeFolder(self, recipe):
        """
            :param recipe: Recipe object

            Creates FoodBuddy/recipes/<ID> directory. 
            Create pdf from URL in directory.
            Create txt file from notes in directory.
        """
        recipePath = os.path.join(self.recipesDirectory, recipe.id) 
        retries = 0
        while os.path.exists(recipePath) and retries < 20:
            recipe.generateNewID()
            retries += 1

        if os.path.exists(recipePath):
            raise OSError("Could not generate a unique ID for recipe.")

        os.makedirs(recipePath)

        pdfPath = os.path.join(recipePath, 'recipe.pdf')
        self._urlToPdf(recipe.url, pdfPath)

        notesPath = os.path.join(recipePath, 'notes.txt')
        with open(notesPath, 'w') as fp:
            fp.write(recipe.notes)

        # TODO: setup thumbnail support
        #if recipe.thumbnail:
        #     copy from added path --> <recipe ID>/thumbnail.<ext>


    def _loadMetadata(self):
        """
            Loads metadata.json into dictionary and returns it.
            Raises IOError if something went wrong loading the file.
        """
        with open(self.metadataDirectory, 'r') as fp:
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
                'pdf': <path to pdf>,
                'notes': <path to notes>,
                'thumbnail': <path to thumbnail>
            }
        """
        pdfPath = os.path.join(recipe.id, 'recipe.pdf')
        notesPath = os.path.join(recipe.id, 'notes.txt')

        data = self._loadMetadata()
        if recipe.id in data['recipes']:
            raise KeyError("This recipe ID already exists in metadata.json.")

        data['recipes'][recipe.id] = {
                'title': recipe.title,
                'tags': recipe.tags,
                'pdf': pdfPath, 
                'notes': notesPath, 
                'thumbnail': recipe.thumbnail,
                }

        with open(self.metadataDirectory, 'w') as fp:
            json.dump(data, fp, indent=4)


    def publishRecipe(self, recipe):
        """
            :param recipe: Recipe object

            Creates recipe on disk.
            Adds recipe to metadata.json.
        """
        self._addRecipeFolder(recipe)
        self._addRecipeMetadata(recipe)


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



        





