from datetime import datetime


def generate_work_summary(user, tasks, work_sessions, activity_logs):
    """
    Generate a daily employee work summary using task updates,
    work sessions, and activity logs.
    """

    today = datetime.utcnow().date()

    # Today's work sessions
    today_sessions = [
        session for session in work_sessions
        if session.start_time and session.start_time.date() == today
    ]

    # Calculate total work duration
    total_work_seconds = 0

    for session in today_sessions:
        if session.start_time:
            end_time = session.end_time or datetime.utcnow()
            total_work_seconds += max(
                0,
                int((end_time - session.start_time).total_seconds())
            )

    work_hours = total_work_seconds // 3600
    work_minutes = (total_work_seconds % 3600) // 60

    # Today's activity
    today_activity = [
        activity for activity in activity_logs
        if activity.timestamp and activity.timestamp.date() == today
    ]

    active_seconds = sum(
        activity.active_seconds or 0
        for activity in today_activity
    )

    idle_seconds = sum(
        activity.idle_seconds or 0
        for activity in today_activity
    )

    # Task information
    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if str(getattr(task, "status", "")).lower() == "completed"
    )

    # Task progress
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
        productivity = 0

    # Summary text
    if not today_sessions and not today_activity:
        summary_text = "No work activity has been recorded for today yet."
    else:
        summary_text = (
            f"{user.name} worked for approximately "
            f"{work_hours} hour(s) and {work_minutes} minute(s) today. "
            f"The employee has {total_tasks} assigned task(s), "
            f"with {completed_tasks} completed. "
            f"Recorded activity shows a productivity level of "
            f"{productivity}% based on active and idle time."
        )

    def format_time(seconds):
        seconds = int(seconds or 0)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return {
        "date": today.strftime("%d-%m-%Y"),
        "total_work_time": format_time(total_work_seconds),
        "active_time": format_time(active_seconds),
        "idle_time": format_time(idle_seconds),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "task_progress": task_progress,
        "productivity_score": productivity,
        "summary": summary_text,
        "work_hours": work_hours,
        "work_minutes": work_minutes,
        "active_seconds": active_seconds,
        "idle_seconds": idle_seconds,
        "productivity": productivity,
    }