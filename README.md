# FoodBuddy
A self-contained app that can save and browse recipes from the web.


# Requirements
- python 3 (add python 3 scripts directory to system path if not already there)

- Has been tested on the following operating systems, although it should work 
on any OS that can run PyQt5:
  - Windows 10
  - Mac OS version 10.12, 10.13, 10.14 
  
- PyQt5
  - pip3 install pyqt5

  
# How to run
After you have the requirements, you can launch the app using run_mac or run_windows
within the launchers/ folder.  Recipes are stored in the data/recipes/ folder which is created
the first time FoodBuddy runs.  Metadata is stored in data/metadata.json to easily find where 
a recipe lives.

NOTE: you may have to update the launchers, depending if Python3 is run with 'py' or 'python3' on your system.