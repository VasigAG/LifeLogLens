import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Activity, get_db, SessionLocal
from typing import Optional, Tuple

class DataHandler:
    def __init__(self):
        self.current_status = "unavailable"
        self.db: Session = SessionLocal()

    def add_entry(self, activity: str, category: str):
        new_entry = Activity(
            activity=activity,
            category=category,
            timestamp=datetime.now()
        )
        self.db.add(new_entry)
        self.db.commit()
        self.current_status = activity

    def get_current_status(self) -> Tuple[str, timedelta]:
        latest = self.db.query(Activity).order_by(Activity.timestamp.desc()).first()
        if not latest:
            return "unavailable", timedelta(0)

        duration = datetime.now() - latest.timestamp
        return latest.activity, duration

    def get_all_activities(self):
        activities = self.db.query(Activity).all()
        if not activities:
            return pd.DataFrame()

        return pd.DataFrame([
            {
                'timestamp': a.timestamp,
                'activity': a.activity,
                'category': a.category
            } for a in activities
        ])

    def search_activity(self, date, time):
        search_datetime = datetime.combine(date, time)
        result = self.db.query(Activity).order_by(
            Activity.timestamp.desc()
        ).all()

        if not result:
            return None

        df = pd.DataFrame([
            {
                'timestamp': r.timestamp,
                'activity': r.activity,
                'category': r.category
            } for r in result
        ])

        closest_idx = abs(pd.to_datetime(df['timestamp']) - search_datetime).idxmin()
        return df.iloc[closest_idx]

    def get_activity_stats(self):
        activities = self.db.query(Activity).all()
        if not activities:
            return pd.DataFrame({'category': [], 'count': []})

        df = pd.DataFrame([{'category': a.category} for a in activities])
        stats = df['category'].value_counts().reset_index()
        stats.columns = ['category', 'count']
        return stats

    def __del__(self):
        self.db.close()