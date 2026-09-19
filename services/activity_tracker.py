from datetime import datetime

from models import db
from models.activity import ActivityLog


def save_activity(
    employee_id,
    session_id,
    active_seconds=0,
    idle_seconds=0,
    keyboard_events=0,
    mouse_events=0
):
    """
    Save one activity-monitoring interval.

    Only activity counts are stored.
    Actual keys pressed or mouse positions are never stored.
    """

    activity = ActivityLog(
        employee_id=employee_id,
        session_id=session_id,
        timestamp=datetime.utcnow(),
        active_seconds=max(0, int(active_seconds)),
        idle_seconds=max(0, int(idle_seconds)),
        keyboard_events=max(0, int(keyboard_events)),
        mouse_events=max(0, int(mouse_events)),
        is_anomaly=False,
        anomaly_score=0.0
    )

    db.session.add(activity)
    db.session.commit()

    return activity


def calculate_activity_percentage(active_seconds, idle_seconds):
    """Calculate percentage of monitored time that was active."""

    active_seconds = max(0, int(active_seconds))
    idle_seconds = max(0, int(idle_seconds))

    total_seconds = active_seconds + idle_seconds

    if total_seconds == 0:
        return 0.0

    return round((active_seconds / total_seconds) * 100, 2)


def get_activity_status(active_seconds, idle_seconds):
    """Return a simple status for an activity interval."""

    percentage = calculate_activity_percentage(
        active_seconds,
        idle_seconds
    )

    if percentage >= 70:
        return "Active"

    if percentage >= 40:
        return "Moderate"

    return "Idle"