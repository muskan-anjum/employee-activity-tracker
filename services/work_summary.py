from datetime import datetime


def calculate_session_work_seconds(session):
    """
    Accurately calculate net work seconds for a session by subtracting breaks.
    """
    if not session.start_time:
        return 0, 0

    end_time = session.end_time or datetime.utcnow()
    raw_duration = max(0, int((end_time - session.start_time).total_seconds()))

    # Calculate break seconds
    break_seconds = 0
    breaks = getattr(session, "breaks", None) or []
    for b in breaks:
        if b.start_time:
            b_end = b.end_time or (datetime.utcnow() if session.end_time is None else session.end_time)
            b_dur = b.duration_seconds if (b.duration_seconds and b.duration_seconds > 0) else max(0, int((b_end - b.start_time).total_seconds()))
            break_seconds += b_dur

    if session.status == "Completed" and session.total_work_seconds and session.total_work_seconds > 0:
        net_work = session.total_work_seconds
    else:
        net_work = max(0, raw_duration - break_seconds)

    return net_work, break_seconds


def generate_work_summary(user, tasks, work_sessions, activity_logs, filter_today=True, period_label="Today"):
    """
    Generate an employee work summary using task updates,
    work sessions, and activity logs.
    Supports both daily mode (filter_today=True) and period mode (filter_today=False).
    """

    today = datetime.utcnow().date()

    if filter_today:
        target_sessions = [
            s for s in work_sessions
            if s.start_time and s.start_time.date() == today
        ]
        target_activity = [
            a for a in activity_logs
            if a.timestamp and a.timestamp.date() == today
        ]
    else:
        target_sessions = list(work_sessions)
        target_activity = list(activity_logs)

    # Calculate total work duration and break duration
    total_work_seconds = 0
    total_break_seconds = 0

    for session in target_sessions:
        net_work, break_sec = calculate_session_work_seconds(session)
        total_work_seconds += net_work
        total_break_seconds += break_sec

    work_hours = total_work_seconds // 3600
    work_minutes = (total_work_seconds % 3600) // 60

    active_seconds = sum(
        activity.active_seconds or 0
        for activity in target_activity
    )

    idle_seconds = sum(
        activity.idle_seconds or 0
        for activity in target_activity
    )

    total_keyboard_events = sum(
        activity.keyboard_events or 0
        for activity in target_activity
    )

    total_mouse_events = sum(
        activity.mouse_events or 0
        for activity in target_activity
    )

    # Task information
    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if str(getattr(task, "status", "")).strip().lower() == "completed"
    )

    task_progress = (
        round((completed_tasks / total_tasks) * 100, 1)
        if total_tasks > 0
        else 0
    )

    # Productivity calculation
    monitored_seconds = active_seconds + idle_seconds

    if monitored_seconds > 0:
        productivity = round(
            (active_seconds / monitored_seconds) * 100,
            1
        )
    else:
        productivity = 0.0

    user_name = getattr(user, "name", "Employee")

    # Generate insightful summary text
    if not target_sessions and not target_activity:
        summary_text = f"No work activity has been recorded for {period_label.lower()} yet."
    else:
        break_mins = total_break_seconds // 60
        break_info = f" with {break_mins} minute(s) of break time" if total_break_seconds > 0 else ""
        summary_text = (
            f"{user_name} recorded approximately {work_hours}h {work_minutes}m of net work{break_info} "
            f"during {period_label.lower()}. Activity monitoring logged {round(active_seconds / 60, 1)} active minute(s) "
            f"yielding a {productivity}% activity score. "
            f"{completed_tasks} of {total_tasks} assigned task(s) are completed ({task_progress}% progress)."
        )

    def format_time(seconds):
        seconds = int(seconds or 0)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return {
        "date": today.strftime("%d-%m-%Y"),
        "period_label": period_label,
        "total_work_time": format_time(total_work_seconds),
        "break_time": format_time(total_break_seconds),
        "active_time": format_time(active_seconds),
        "idle_time": format_time(idle_seconds),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "task_progress": task_progress,
        "productivity_score": productivity,
        "summary": summary_text,
        "work_hours": work_hours,
        "work_minutes": work_minutes,
        "total_work_seconds": total_work_seconds,
        "total_break_seconds": total_break_seconds,
        "active_seconds": active_seconds,
        "idle_seconds": idle_seconds,
        "total_keyboard_events": total_keyboard_events,
        "total_mouse_events": total_mouse_events,
        "productivity": productivity,
    }