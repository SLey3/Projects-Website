# ------------------ Import ------------------
import pandas as pd
import os
import datetime

# ------------------ ModHistory Source code ------------------
class ModHistory:
    """
    Modification History class
    """
    def __init__(self, filename, timestamp):
        current_path = os.path.abspath('.')
        try:
            assert os.path.basename(current_path) == 'mod_history'
        except AssertionError:
            if os.path.basename(current_path) == 'Projects_Website':
                os.chdir('./src/mod_history')
            elif os.path.basename(current_path) == 'src':
                os.chdir('./mod_history')

        del current_path
        self.file = filename
        self.timestamp = timestamp
    
    def insert_history(self):
        """
        Inserts file history data to csv file
        """
        print(self.file)
        print(self.timestamp)
        df = pd.DataFrame({"filename": [self.file], "timestamp": [self.timestamp]}, dtype='category')
        df.to_csv("modifications.csv", encoding="utf-8", mode='a', header=False)
    
    def update_history(self, new_file_name = None, new_timestamp = None):
        """
        Updates file history
        """
        if new_file_name is not None:
            file_history_log = []
        if new_timestamp is not None:
            time_history_log = []
        if new_file_name and new_timestamp is None:
            raise ValueError("Only one value can be None")
        csv_data = pd.read_csv("modifications.csv", dtype="category", encoding="utf-8", engine="python", cache_dates=False)
        
    
    @staticmethod
    def history(path):
        """
        Gets file modfication history
        
        Returns:
            history
        """
        os.chdir(path)
        history = {}
        csv_data = pd.read_csv("modifications.csv", dtype="category", encoding="utf-8", engine="python", cache_dates=False)
        for i in range(len(csv_data)):
            fileData = csv_data.values[i][1]
            timeData = csv_data.values[i][2]
            history.setdefault("file", []).append(fileData)
            history.setdefault("timestamp", []).append(timeData)
        return history