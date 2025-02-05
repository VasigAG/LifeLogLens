import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Activity, get_db, SessionLocal
from typing import Optional, Tuple
import pytz

class DataHandler:
    def __init__(self):
        self.current_status = "unavailable"
        self.db: Session = SessionLocal()

    def add_entry(self, activity: str, category: str):
        # Update duration of previous activity
        previous = self.db.query(Activity).order_by(Activity.timestamp.desc()).first()
        if previous and previous.duration is None:
            previous.duration = datetime.now() - previous.timestamp
            self.db.commit()

        # Add new activity
        new_entry = Activity(
            activity=activity,
            category=category,
            timestamp=datetime.now(),
            duration=None  # Will be updated when next activity is logged
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

    def get_recent_activities(self, limit: int = 10):
        activities = self.db.query(Activity).order_by(Activity.timestamp.desc()).limit(limit).all()
        if not activities:
            return pd.DataFrame()

        return pd.DataFrame([
            {
                'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M'),
                'activity': a.activity,
                'category': a.category,
                'duration': str(a.duration) if a.duration else 'ongoing'
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
            return pd.DataFrame({'category': [], 'total_hours': []})

        # Calculate total duration per category
        category_durations = {}
        for activity in activities:
            duration = activity.duration or (datetime.now() - activity.timestamp)
            if activity.category not in category_durations:
                category_durations[activity.category] = duration
            else:
                category_durations[activity.category] += duration

        # Convert to hours and create DataFrame
        stats = pd.DataFrame([
            {
                'category': category,
                'total_hours': duration.total_seconds() / 3600
            }
            for category, duration in category_durations.items()
        ])
        return stats

    def __del__(self):
        self.db.close()