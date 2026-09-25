from datetime import datetime

from models import LoginSession, WorkSession
from services.work_summary import calculate_session_work_seconds


def revoke_employee_sessions(employee_id, stop_work=False):
    """Revoke every browser login; optionally close work and breaks atomically."""
    now = datetime.utcnow()
    for record in LoginSession.query.filter_by(user_id=employee_id, logout_time=None):
        record.logout_time = now
        record.is_online = False
        record.duration_seconds = max(0, int((now - record.login_time).total_seconds()))
    if stop_work:
        for work in WorkSession.query.filter_by(employee_id=employee_id, end_time=None):
            work.end_time = now
            for pause in work.breaks:
                if pause.end_time is None:
                    pause.end_time = now
                    pause.duration_seconds = max(0, int((now - pause.start_time).total_seconds()))
            work.total_work_seconds = calculate_session_work_seconds(work)[0]
            work.status = "Terminated"
