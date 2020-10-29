# ------------------ Import ------------------
import pandas as pd
import os
import datetime
from typing import Optional

# ------------------ ModHistory Source code ------------------
class ModHistory:
    """
    Modification History class
    """
    def __init__(self, filename: str = None, timestamp: str = None):
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
        df = pd.DataFrame({"filename": [self.file], "timestamp": [self.timestamp]}, dtype='category')
        df.to_csv("modifications.csv", encoding="utf-8", mode='a', header=False)
    
    def update_history(self, new_file_name: Optional[str] = None, new_timestamp: Optional[str] = None):
        """
        Updates file history
        """
        file_history_log = []
        time_history_log = []
        csv_data = pd.read_csv("modifications.csv", dtype="category", encoding="utf-8", engine="c", cache_dates=False)
        for i in range(len(csv_data)):
            file_history_log.append(csv_data.values[i][1])
            time_history_log.append(csv_data.values[i][2])
        file_index = 0
        for file_name in file_history_log:
            if self.file == file_name:
                file_history_log.insert(file_index, new_file_name)
            file_index += 1
        del file_index
        time_index = 0
        for timestamp_name in time_history_log:
            if self.timestamp == timestamp_name:
                time_history_log.insert(time_index, new_timestamp)
            time_index +=1
           
        del time_index 
        
        def temp_delete(file_log):
            data = pd.read_csv("modifications.csv", index_col="filename", dtype="category", encoding="utf-8", engine="c", cache_dates=False)
            data.drop(file_log, inplace=True)
            
        temp_delete(file_history_log)
        
        df = pd.DataFrame({"filename": file_history_log, "timestamp": time_history_log}, dtype='category')
        df.to_csv("modifications.csv", encoding="utf-8", mode='a', header=False)
    
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
    
# hist = ModHistory("__init__.py", "2020-10-26 19:01:10")
# hist.update_history()