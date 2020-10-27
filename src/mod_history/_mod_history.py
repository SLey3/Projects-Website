# ------------------ Import ------------------
import pandas as pd
import os

# ------------------ Path Config ------------------
current_path = os.path.abspath('.')
try:
    assert os.path.basename(current_path) == 'mod_history'
except AssertionError:
    if os.path.basename(current_path) == 'Projects_Website':
        os.chdir('./src/mod_history')
    elif os.path.basename(current_path) == 'src':
        os.chdir('./mod_history')

del current_path


# ------------------ ModHistory Source code ------------------
class ModHistory:
    """
    Modification History class
    """
    def __init__(self, filename: str = None, timestamp: str = None):
        self.file = filename
        self.timestamp = timestamp
    
    def insert_history(self):
        """
        Inserts file history data to csv file
        """
        df = pd.DataFrame({"filename": [self.file], "timestamp": [self.timestamp]}, dtype='category')
        df.to_csv("modifications.csv", encoding="utf-8", mode='a', header=False)
    
    @staticmethod
    def history():
        """
        Gets file modfication history
        
        Returns:
            history
        """
        history = {}
        csv_data = pd.read_csv("modifications.csv", dtype="category", encoding="utf-8", engine="python", cache_dates=False)
        for i in range(len(csv_data)):
            fileData = csv_data.values[i][1]
            timeData = csv_data.values[i][2]
            history.setdefault("file", []).append(fileData)
            history.setdefault("timestamp", []).append(timeData)
        return history