import pandas as pd
from datetime import datetime
import json
import os

class DataHandler:
    def __init__(self):
        self.data_file = "life_log.json"
        self.current_status = "unavailable"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = pd.DataFrame(json.load(f))
        else:
            self.data = pd.DataFrame(columns=['timestamp', 'activity', 'category'])
            self.save_data()

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data.to_dict('records'), f)

    def add_entry(self, activity, category):
        new_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'category': category
        }
        self.data = pd.concat([self.data, pd.DataFrame([new_entry])], ignore_index=True)
        self.current_status = activity
        self.save_data()

    def get_current_status(self):
        if len(self.data) > 0:
            return self.data.iloc[-1]['activity']
        return "unavailable"

    def search_activity(self, date, time):
        search_datetime = f"{date} {time}"
        try:
            search_dt = pd.to_datetime(search_datetime)
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            closest_idx = abs(self.data['timestamp'] - search_dt).idxmin()
            return self.data.iloc[closest_idx]
        except:
            return None

    def get_activity_stats(self):
        if len(self.data) == 0:
            return pd.DataFrame()
        return self.data['category'].value_counts().reset_index()
