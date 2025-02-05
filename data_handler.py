import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Activity, get_db, SessionLocal
from typing import Optional, Tuple
import pytz

def format_duration(duration):
    """Format timedelta into readable string"""
    if not duration:
        return 'ongoing'

    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

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

    def delete_entry(self, entry_id: int):
        entry = self.db.query(Activity).filter(Activity.id == entry_id).first()
        if entry:
            self.db.delete(entry)
            self.db.commit()
            return True
        return False

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

        data = []
        for i, a in enumerate(activities):
            duration = a.duration
            if i == 0:  # For the most recent activity
                duration = datetime.now() - a.timestamp

            data.append({
                'id': a.id,
                'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M'),
                'activity': a.activity,
                'category': a.category,
                'duration': format_duration(duration)
            })

        return pd.DataFrame(data)

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