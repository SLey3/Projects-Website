# ------------------ Imports ------------------
import datetime
import os
from typing import List
from mod_history import ModHistory

# ------------------ Modified() Global Variable ------------------

MOD_FILES = []

FOLDERS = ["src", ".vscode", ".git", "__pycache__", "templates", "public", "assets", "render", "web_util"]
    
# ------------------ Modified() Source ------------------
def Modified():
    """
    Returns the modified files
    """
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
    _history = ModHistory.history(os.path.abspath('./src/mod_history'))
    os.chdir('../..')
    PARENT_DIR = os.path.abspath('.')
    print(os.listdir(PARENT_DIR))
    for file in os.listdir(PARENT_DIR):
        print(file)
        modTime = os.path.getmtime(file)
        current = datetime.datetime.fromtimestamp(modTime).strftime('%Y-%m-%d %H:%M:%S')
        history = _history
        for file_name, timestamp in history.items():
            if current == timestamp and file == file_name:
                continue
            else:
                if current != timestamp and file == file_name:
                    MOD_FILES.append(file)
                    # Code for updating csv file here
                elif file != file_name:
                    if file in FOLDERS:
                        continue
                    else:
                        history_manager = ModHistory(file, current)
                        history_manager.insert_history()
                        os.chdir('../..')
    subfolders = [f.path for f in os.scandir(PARENT_DIR) if f.is_dir()]
    
    
Modified()