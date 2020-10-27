# ------------------ Imports ------------------
import datetime
import os
from typing import List
from mod_history import ModHistory

# ------------------ Modified() Global Variable ------------------

MOD_FILES = []

history_manager = ModHistory()

try:
    PARENT_DIR = os.path.abspath('.')
    assert os.path.basename(PARENT_DIR) == 'Projects_Website'
except AssertionError:
    in_dir = False
    while not in_dir:
        os.chdir('..')
        PARENT_DIR = os.path.abspath('.')
        try:
            assert os.path.basename(PARENT_DIR) == 'Projects_Website'
            in_dir = True
            break
        except AssertionError:
            continue
    
# ------------------ Modified() Source ------------------
def Modified():
    """
    Returns the modified files
    """
    for file in os.listdir(PARENT_DIR):
        modTime = os.path.getmtime(file)
        current = datetime.datetime.fromtimestamp(modTime).strftime('%Y-%m-%d %H:%M:%S')
    subfolders = [f.path for f in os.scandir(PARENT_DIR) if f.is_dir()]