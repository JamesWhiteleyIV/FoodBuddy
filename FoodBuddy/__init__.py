import os

RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_DIR = os.path.abspath(os.path.join(RESOURCE_DIR, 'resources'))

from FoodBuddy.main import *