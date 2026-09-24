from datetime import datetime

from models import db
from models.activity import ActivityLog
from services.ml_analyzer import evaluate_single_heuristic


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
    act_sec = max(0, int(active_seconds))
    idle_sec = max(0, int(idle_seconds))
    kb_ev = max(0, int(keyboard_events))
    ms_ev = max(0, int(mouse_events))

    # Evaluate heuristic anomaly indicators for the interval
    temp_obj = type("TempActivity", (), {
        "active_seconds": act_sec,
        "idle_seconds": idle_sec,
        "keyboard_events": kb_ev,
        "mouse_events": ms_ev,
    })()
    eval_result = evaluate_single_heuristic(temp_obj)

    activity = ActivityLog(
        employee_id=employee_id,
        session_id=session_id,
        timestamp=datetime.utcnow(),
        active_seconds=act_sec,
        idle_seconds=idle_sec,
        keyboard_events=kb_ev,
        mouse_events=ms_ev,
        is_anomaly=eval_result.get("is_anomaly", False),
        anomaly_score=eval_result.get("anomaly_score", 0.0),
        anomaly_reason=eval_result.get("reason", "Standard workforce interaction.")
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