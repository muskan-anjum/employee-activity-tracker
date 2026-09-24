from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import User, db
from models.project import Project
from models.task import Task
from models.work_session import WorkSession
from models.activity import ActivityLog
from services.ml_analyzer import analyze_activity


dashboard_bp = Blueprint("dashboard", __name__)


def role_required(role):
    def decorator(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            if current_user.role != role:
                flash("You are not authorized to access this page.", "danger")
                return redirect(url_for("dashboard.employee_dashboard"))

            return function(*args, **kwargs)

        return wrapped_function
    return decorator


@dashboard_bp.route("/employee/dashboard")
@login_required
@role_required("employee")
def employee_dashboard():
    from models.work_session import WorkSession, Break
    from models.activity import ActivityLog
    from services.work_summary import generate_work_summary

    tasks = Task.query.filter_by(employee_id=current_user.id).all()

    active_session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).order_by(WorkSession.start_time.desc()).first()

    active_break = None

    if active_session:
        active_break = Break.query.filter_by(
            session_id=active_session.id,
            end_time=None
        ).first()

    work_sessions = WorkSession.query.filter_by(
        employee_id=current_user.id
    ).all()

    activity_logs = ActivityLog.query.filter_by(
        employee_id=current_user.id
    ).all()

    work_summary = generate_work_summary(
        current_user,
        tasks,
        work_sessions,
        activity_logs
    )
    projects = Project.query.all()
    return render_template(
        "employee_dashboard.html",
        user=current_user,
        tasks=tasks,
        active_session=active_session,
        active_break=active_break,
        work_summary=work_summary,
        projects=projects
    )
@dashboard_bp.route("/employee/projects")
@login_required
@role_required("employee")
def employee_projects():
    projects = (
    Project.query
    .join(Task, Task.project_id == Project.id)
    .filter(Task.employee_id == current_user.id)
    .distinct()
    .all()
)
    project_times = {}

    for project in projects:
        sessions = WorkSession.query.filter_by(
            employee_id=current_user.id,
            project_id=project.id
        ).all()

        project_times[project.id] = sum(
            session.total_work_seconds or 0
            for session in sessions
        )

    return render_template(
        "employee_projects.html",
        projects=projects,
        project_times=project_times
    )


@dashboard_bp.route("/employee/activity-history")
@login_required
@role_required("employee")
def employee_activity_history():
    from models.activity import ActivityLog

    activities = ActivityLog.query.filter_by(
        employee_id=current_user.id
    ).all()

    return render_template(
        "employee_activity_history.html",
        activities=activities
    )
@dashboard_bp.route("/employee/work-summary")
@login_required
@role_required("employee")
def employee_work_summary():
    from models.work_session import WorkSession, Break
    from models.activity import ActivityLog
    from services.work_summary import generate_work_summary

    tasks = Task.query.filter_by(employee_id=current_user.id).all()

    work_sessions = WorkSession.query.filter_by(
        employee_id=current_user.id
    ).all()

    activity_logs = ActivityLog.query.filter_by(
        employee_id=current_user.id
    ).all()

    work_summary = generate_work_summary(
        current_user,
        tasks,
        work_sessions,
        activity_logs
    )

    return render_template(
        "employee_work_summary.html",
        user=current_user,
        work_summary=work_summary
    )
@dashboard_bp.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    from datetime import datetime, timedelta
    from models.work_session import WorkSession
    from models.activity import ActivityLog
    from services.ml_analyzer import analyze_activity

    # Employees
    employees = User.query.filter_by(role="employee").all()
    total_employees = len(employees)

    # Current work sessions
    active_sessions = WorkSession.query.filter_by(end_time=None).all()

    currently_working = sum(
        1 for session in active_sessions
        if session.status == "Working"
    )

    on_break = sum(
        1 for session in active_sessions
        if session.status == "On Break"
    )

    # Active projects
    active_projects = Project.query.filter_by(status="Active").count()

    # Latest activity records
    recent_logs = (
        ActivityLog.query
        .order_by(ActivityLog.timestamp.desc())
        .limit(100)
        .all()
    )

    # AI anomaly analysis
    analysis_results = analyze_activity(recent_logs)

    unusual_count = sum(
        1 for result in analysis_results
        if result.get("status") == "Unusual"
    )

    # Overall productivity
    total_active_seconds = sum(
        log.active_seconds or 0 for log in recent_logs
    )

    total_idle_seconds = sum(
        log.idle_seconds or 0 for log in recent_logs
    )

    monitored_seconds = total_active_seconds + total_idle_seconds

    if monitored_seconds > 0:
        average_productivity = round(
            (total_active_seconds / monitored_seconds) * 100,
            1
        )
    else:
        average_productivity = 0

    # Last 7 days activity
    weekly_labels = []
    weekly_activity = []

    today = datetime.utcnow().date()

    for days_ago in range(6, -1, -1):
        day = today - timedelta(days=days_ago)

        day_logs = [
            log for log in recent_logs
            if log.timestamp and log.timestamp.date() == day
        ]

        active_seconds = sum(
            log.active_seconds or 0 for log in day_logs
        )

        idle_seconds = sum(
            log.idle_seconds or 0 for log in day_logs
        )

        total_seconds = active_seconds + idle_seconds

        if total_seconds > 0:
            activity_percentage = round(
                (active_seconds / total_seconds) * 100,
                1
            )
        else:
            activity_percentage = 0

        weekly_labels.append(day.strftime("%a"))
        weekly_activity.append(activity_percentage)

    return render_template(
        "admin_dashboard.html",
        user=current_user,
        total_employees=total_employees,
        currently_working=currently_working,
        on_break=on_break,
        active_projects=active_projects,
        unusual_count=unusual_count,
        average_productivity=average_productivity,
        recent_logs=recent_logs,
        weekly_labels=weekly_labels,
        weekly_activity=weekly_activity
    )

@dashboard_bp.route("/admin/employees", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_employees():
    if request.method == "POST":
        name = request.form.get("name")         
        email = request.form.get("email")
        password = request.form.get("password")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "error")
        else:
                employee = User(
            name=name,
            email=email,
            role="employee",
            is_active_account=True
        )
                employee.set_password(password)

                db.session.add(employee)
                db.session.commit()

                flash("Employee added successfully.", "success")
                return redirect(url_for("dashboard.admin_employees"))
    employees = User.query.filter_by(role="employee").all()

    return render_template(
        "admin_employees.html",
        user=current_user,
        employees=employees
    )
@dashboard_bp.route("/admin/projects", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_projects():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if name:
            project = Project(
                name=name,
                description=description,
                status="Active"
            )
            db.session.add(project)
            db.session.commit()

            flash("Project created successfully.", "success")
            return redirect(url_for("dashboard.admin_projects"))

    projects = Project.query.all()
    tasks = Task.query.all()
    employees = User.query.filter_by(role="employee").all()

    return render_template(
        "admin_projects.html",
        user=current_user,
        projects=projects,
        tasks=tasks,
        employees=employees
    )

@dashboard_bp.route("/admin/tasks", methods=["POST"])
@login_required
@role_required("admin")
def create_task():
    title = request.form.get("title")
    project_id = request.form.get("project_id")
    employee_id = request.form.get("employee_id")

    if title and project_id and employee_id:
        task = Task(
            title=title,
            project_id=int(project_id),
            employee_id=int(employee_id),
            status="Pending"
        )

        db.session.add(task)
        db.session.commit()

        flash("Task created successfully.", "success")

    return redirect(url_for("dashboard.admin_projects"))

@dashboard_bp.route("/employee/task/<int:task_id>/update", methods=["POST"])
@login_required
@role_required("employee")
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.employee_id != current_user.id:
        flash("You are not authorized to update this task.", "danger")
        return redirect(url_for("dashboard.employee_dashboard"))

    status = request.form.get("status")
    progress = request.form.get("progress")

    if status:
        task.status = status

    if progress is not None:
        try:
            progress_value = int(progress)

            if 0 <= progress_value <= 100:
                task.progress = progress_value

                if progress_value == 100:
                    task.status = "Completed"
                elif progress_value > 0 and task.status == "Completed":
                    task.status = "In Progress"
            else:
                flash("Progress must be between 0 and 100.", "danger")
                return redirect(url_for("dashboard.employee_dashboard"))

        except ValueError:
            flash("Progress must be a valid number.", "danger")
            return redirect(url_for("dashboard.employee_dashboard"))

    db.session.commit()
    flash("Task updated successfully.", "success")

    return redirect(url_for("dashboard.employee_dashboard"))

@dashboard_bp.route("/employee/work/start", methods=["POST"])
@login_required
@role_required("employee")
def start_work():
    from models.work_session import WorkSession
    from models.project import Project
    from datetime import datetime

    existing_session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).first()

    if existing_session:
        return jsonify({
            "success": False,
            "message": "A work session is already active."
        }), 400

    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id")

    if project_id:
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid project selected."
            }), 400

        project = db.session.get(Project, project_id)

        if not project:
            return jsonify({
                "success": False,
                "message": "Selected project was not found."
            }), 404
    else:
        project_id = None

    session = WorkSession(
        employee_id=current_user.id,
        project_id=project_id,
        start_time=datetime.utcnow(),
        status="Working"
    )

    db.session.add(session)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Work session started successfully.",
        "session_id": session.id,
        "project_id": project_id
    })
@dashboard_bp.route("/employee/work/break", methods=["POST"])
@login_required
@role_required("employee")
def start_break():
    from models.work_session import WorkSession, Break

    session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).order_by(WorkSession.start_time.desc()).first()

    if not session:
        return jsonify({
            "success": False,
            "message": "No active work session"
        }), 400

    active_break = Break.query.filter_by(
        session_id=session.id,
        end_time=None
    ).first()

    if active_break:
        return jsonify({
            "success": False,
            "message": "Break already active"
        }), 400

    new_break = Break(session_id=session.id)
    session.status = "On Break"

    db.session.add(new_break)
    db.session.commit()

    return jsonify({
    "success": True,
    "message": "Break started successfully"
})
@dashboard_bp.route("/employee/work/end-break", methods=["POST"])
@login_required
@role_required("employee")
def end_break():
    from datetime import datetime
    from models.work_session import WorkSession, Break

    session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).order_by(WorkSession.start_time.desc()).first()

    if not session:
        return jsonify({"success": False, "message": "No active work session"}), 400

    active_break = Break.query.filter_by(
        session_id=session.id,
        end_time=None
    ).first()

    if not active_break:
        return jsonify({"success": False, "message": "No active break"}), 400

    active_break.end_time = datetime.utcnow()
    active_break.duration_seconds = max(
        0,
        int((active_break.end_time - active_break.start_time).total_seconds())
    )
    session.status = "Working"

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Break ended successfully"
    })
@dashboard_bp.route("/admin/activity")
@login_required
@role_required("admin")
def admin_activity():
    # Get all currently open work sessions
    active_sessions = WorkSession.query.filter_by(end_time=None).all()

    # Count employees currently working
    currently_working = sum(
        1 for session in active_sessions
        if session.status == "Working"
    )

    # Count employees currently on break
    on_break = sum(
        1 for session in active_sessions
        if session.status == "On Break"
    )

    # Get recent activity records
    recent_logs = (
        ActivityLog.query
        .order_by(ActivityLog.timestamp.desc())
        .limit(50)
        .all()
    )

    # Find employees whose recent activity is more idle than active
    idle_employee_ids = {
        log.employee_id
        for log in recent_logs
        if (log.idle_seconds or 0) > (log.active_seconds or 0)
    }

    idle_employees = len(idle_employee_ids)

    # Run ML anomaly analysis
    analysis_results = analyze_activity(recent_logs)

    activity_alerts = sum(
        1 for result in analysis_results
        if result.get("status") == "Unusual"
    )

    return render_template(
        "admin_activity.html",
        user=current_user,
        currently_working=currently_working,
        on_break=on_break,
        idle_employees=idle_employees,
        activity_alerts=activity_alerts,
        recent_logs=recent_logs
    )
@dashboard_bp.route("/admin/ai-analysis")
@login_required
@role_required("admin")
def admin_ai_analysis():
    from models.activity import ActivityLog
    from services.ml_analyzer import analyze_activity

    activity_records = ActivityLog.query.order_by(
        ActivityLog.timestamp.desc()
    ).limit(100).all()

    analysis_results = analyze_activity(activity_records)

    unusual_count = sum(
        1 for result in analysis_results
        if result["status"] == "Unusual"
    )

    return render_template(
        "admin_ai_analysis.html",
        user=current_user,
        analysis_results=analysis_results,
        unusual_count=unusual_count,
        total_analyzed=len(analysis_results)
    )
@dashboard_bp.route("/admin/reports")
@login_required
@role_required("admin")
def admin_reports():
    from datetime import datetime, timedelta

    from models.user import User
    from models.task import Task
    from models.work_session import WorkSession
    from models.activity import ActivityLog
    from services.work_summary import generate_work_summary

    # Report period: daily, weekly or monthly
    period = request.args.get("period", "daily").lower()

    if period not in ["daily", "weekly", "monthly"]:
        period = "daily"

    now = datetime.utcnow()

    if period == "weekly":
        start_date = now - timedelta(days=7)
        period_label = "Last 7 Days"

    elif period == "monthly":
        start_date = now - timedelta(days=30)
        period_label = "Last 30 Days"

    else:
        start_date = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        period_label = "Today"

    employees = User.query.filter_by(role="employee").all()
    reports = []

    for employee in employees:

        tasks = Task.query.filter_by(
            employee_id=employee.id
        ).all()

        sessions = (
            WorkSession.query
            .filter(
                WorkSession.employee_id == employee.id,
                WorkSession.start_time >= start_date
            )
            .all()
        )

        activity_logs = (
            ActivityLog.query
            .filter(
                ActivityLog.employee_id == employee.id,
                ActivityLog.timestamp >= start_date
            )
            .all()
        )

        summary = generate_work_summary(
            employee,
            tasks,
            sessions,
            activity_logs
        )

        reports.append({
            "employee": employee,
            "work_time": summary.get(
                "total_work_time",
                "00:00:00"
            ),
            "active_time": summary.get(
                "active_time",
                "00:00:00"
            ),
            "idle_time": summary.get(
                "idle_time",
                "00:00:00"
            ),
            "productivity": summary.get(
                "productivity_score",
                0
            )
        })

    return render_template(
        "admin_reports.html",
        user=current_user,
        reports=reports,
        selected_period=period,
        period_label=period_label
    )
@dashboard_bp.route("/admin/reports/export")
@login_required
@role_required("admin")
def export_admin_reports():
    import csv
    import io
    from flask import Response

    from models.user import User
    from models.task import Task
    from models.work_session import WorkSession
    from models.activity import ActivityLog
    from services.work_summary import generate_work_summary

    employees = User.query.filter_by(role="employee").all()

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV headings
    writer.writerow([
        "Employee",
        "Email",
        "Work Time",
        "Active Time",
        "Idle Time",
        "Activity Score"
    ])

    # Real employee report data
    for employee in employees:
        summary = generate_work_summary(
            employee,
            Task.query.filter_by(employee_id=employee.id).all(),
            WorkSession.query.filter_by(employee_id=employee.id).all(),
            ActivityLog.query.filter_by(employee_id=employee.id).all()
        )

        writer.writerow([
            employee.name,
            employee.email,
            summary.get("total_work_time", "00:00:00"),
            summary.get("active_time", "00:00:00"),
            summary.get("idle_time", "00:00:00"),
            f'{summary.get("productivity_score", 0)}%'
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=workai_employee_report.csv"
        }
    )
@dashboard_bp.route("/employee/activity", methods=["POST"])
@login_required
@role_required("employee")
def record_employee_activity():
    from flask import request, jsonify
    from models.work_session import WorkSession
    from services.activity_tracker import save_activity

    # Find the employee's current working session
    session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).order_by(WorkSession.start_time.desc()).first()

    if not session:
        return jsonify({
            "success": False,
            "message": "No active work session"
        }), 200
    # Pause activity tracking while employee is on break
    if session.status == "On Break":
        return jsonify({
            "success": False,
            "message": "Activity tracking paused during break"
        }), 200

    data = request.get_json(silent=True) or {}

    try:
        activity = save_activity(
            employee_id=current_user.id,
            session_id=session.id,
            active_seconds=data.get("active_seconds", 0),
            idle_seconds=data.get("idle_seconds", 0),
            keyboard_events=data.get("keyboard_events", 0),
            mouse_events=data.get("mouse_events", 0)
        )

        return jsonify({
            "success": True,
            "activity_id": activity.id
        }), 201

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid activity data"
        }), 400
@dashboard_bp.route("/employee/end-work", methods=["POST"])
@login_required
@role_required("employee")
def end_work():
    from datetime import datetime
    from models import db
    from models.work_session import WorkSession, Break

    # Find active work session
    session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).first()

    if not session:
        return jsonify({
            "success": False,
            "message": "No active work session"
        }), 400

    # Use the same timezone style as the session start time
    if session.start_time and session.start_time.tzinfo:
        session.end_time = datetime.now(session.start_time.tzinfo)
    else:
        session.end_time = datetime.utcnow()

    # Close active break, if employee ends work while on break
    active_break = Break.query.filter_by(
        session_id=session.id,
        end_time=None
    ).first()

    if active_break:
        active_break.end_time = session.end_time

        if active_break.start_time:
            active_break.duration_seconds = max(
                0,
                int(
                    (active_break.end_time - active_break.start_time)
                    .total_seconds()
                )
            )
        else:
            active_break.duration_seconds = 0

    # Calculate full session duration
    session_duration_seconds = 0

    if session.start_time:
        session_duration_seconds = max(
            0,
            int(
                (session.end_time - session.start_time)
                .total_seconds()
            )
        )

    # Calculate total break duration
    all_breaks = Break.query.filter_by(
        session_id=session.id
    ).all()

    total_break_seconds = sum(
        break_item.duration_seconds or 0
        for break_item in all_breaks
    )

    # Actual work time = full session - breaks
    session.total_work_seconds = max(
        0,
        session_duration_seconds - total_break_seconds
    )

    session.status = "Completed"

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Work session ended successfully",
        "total_work_seconds": session.total_work_seconds,
        "break_seconds": total_break_seconds
    })
@dashboard_bp.route("/admin/assistant", methods=["POST"])
@login_required
@role_required("admin")
def workai_assistant():
    from models.activity import ActivityLog
    from models.user import User
    from models.work_session import WorkSession
    from services.ml_analyzer import analyze_activity

    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip().lower()

    if not question:
        return jsonify({
            "success": False,
            "answer": "Please enter a question."
        }), 400

    recent_logs = (
        ActivityLog.query
        .order_by(ActivityLog.timestamp.desc())
        .limit(100)
        .all()
    )

    analysis_results = analyze_activity(recent_logs)

    unusual_results = [
        result for result in analysis_results
        if result.get("status") == "Unusual"
    ]

    unusual_count = len(unusual_results)

    total_active = sum(
        log.active_seconds or 0
        for log in recent_logs
    )

    total_idle = sum(
        log.idle_seconds or 0
        for log in recent_logs
    )

    total_time = total_active + total_idle

    activity_percentage = (
        round((total_active / total_time) * 100, 1)
        if total_time > 0
        else 0
    )

    active_sessions = WorkSession.query.filter_by(
        end_time=None
    ).all()

    working_count = sum(
        1 for session in active_sessions
        if session.status == "Working"
    )

    break_count = sum(
        1 for session in active_sessions
        if session.status == "On Break"
    )

    # Unusual activity
    if (
        "unusual" in question
        or "anomaly" in question
        or "alert" in question
    ):
        employee_ids = {
            result["record"].employee_id
            for result in unusual_results
            if result.get("record")
        }

        employee_names = []

        for employee_id in employee_ids:
            employee = User.query.get(employee_id)

            if employee:
                name = getattr(employee, "name", None)

                if not name:
                    name = getattr(
                        employee,
                        "email",
                        f"Employee #{employee_id}"
                    )

                employee_names.append(name)

        if unusual_count == 0:
            answer = (
                f"The Isolation Forest model analyzed "
                f"{len(recent_logs)} recent activity records "
                f"and found no model-flagged unusual patterns."
            )

        elif employee_names:
            answer = (
                f"The Isolation Forest model analyzed "
                f"{len(recent_logs)} recent activity records and "
                f"flagged {unusual_count} unusual activity record(s). "
                f"The flagged records belong to: "
                f"{', '.join(employee_names)}. "
                f"These are model-flagged patterns and should be "
                f"reviewed with additional context."
            )

        else:
            answer = (
                f"The Isolation Forest model analyzed "
                f"{len(recent_logs)} recent activity records and "
                f"flagged {unusual_count} unusual activity record(s)."
            )

    # Idle activity
    elif "idle" in question:
        employee_idle_data = {}

        for log in recent_logs:
            employee_id = log.employee_id

            if employee_id not in employee_idle_data:
                employee_idle_data[employee_id] = {
                    "active": 0,
                    "idle": 0
                }

            employee_idle_data[employee_id]["active"] += (
                log.active_seconds or 0
            )

            employee_idle_data[employee_id]["idle"] += (
                log.idle_seconds or 0
            )

        high_idle_employees = []

        for employee_id, stats in employee_idle_data.items():
            if stats["idle"] > stats["active"]:
                employee = User.query.get(employee_id)

                if employee:
                    name = getattr(employee, "name", None)

                    if not name:
                        name = getattr(
                            employee,
                            "email",
                            f"Employee #{employee_id}"
                        )

                    high_idle_employees.append(name)

        if high_idle_employees:
            answer = (
                f"Based on the latest {len(recent_logs)} activity "
                f"records, employees with more idle time than active "
                f"time are: {', '.join(high_idle_employees)}. "
                f"Across all recent records, active time is "
                f"{total_active} seconds and idle time is "
                f"{total_idle} seconds."
            )

        else:
            answer = (
                f"Based on the latest {len(recent_logs)} activity "
                f"records, no employee has more idle time than "
                f"active time. Total active time is "
                f"{total_active} seconds and total idle time is "
                f"{total_idle} seconds."
            )

    # Working / break status
    elif "working" in question or "break" in question:
        answer = (
            f"There are currently {working_count} employee "
            f"session(s) working and {break_count} session(s) "
            f"on break."
        )

    # Activity percentage
    elif (
        "productivity" in question
        or "performance" in question
        or "activity percentage" in question
    ):
        answer = (
            f"Based on the latest {len(recent_logs)} activity "
            f"records, the activity percentage is "
            f"{activity_percentage}%. The Isolation Forest model "
            f"flagged {unusual_count} unusual activity record(s)."
        )

    # Workforce summary
    elif (
        "summary" in question
        or "today" in question
        or "workforce" in question
    ):
        answer = (
            f"WorkAI analyzed {len(recent_logs)} recent activity "
            f"records. Activity percentage is "
            f"{activity_percentage}%. {working_count} employee "
            f"session(s) are currently working, {break_count} "
            f"are on break, and the Isolation Forest model "
            f"flagged {unusual_count} unusual activity record(s)."
        )
        # Project intelligence
    elif "project" in question:
        project_sessions = WorkSession.query.filter(
            WorkSession.project_id.isnot(None)
        ).all()

        project_totals = {}

        for session in project_sessions:
            seconds = session.total_work_seconds or 0
            project_totals[session.project_id] = (
                project_totals.get(session.project_id, 0) + seconds
            )

        if not project_totals:
            answer = (
                "No project-linked tracked time is available yet. "
                "Start a work session with a project selected to build "
                "project-wise time intelligence."
            )
        else:
            top_project_id = max(
                project_totals,
                key=project_totals.get
            )

            from models.project import Project

            top_project = Project.query.filter_by(
                id=top_project_id
            ).first()

            total_seconds = project_totals[top_project_id]

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            project_name = (
                top_project.name
                if top_project
                else f"Project #{top_project_id}"
            )

            answer = (
                f"{project_name} currently has the highest recorded "
                f"project-linked work time: "
                f"{hours:02d}:{minutes:02d}:{seconds:02d}."
            )

    # Help
    else:
        answer = (
            "I can answer questions about workforce activity, "
            "idle time, activity percentage, current working "
            "sessions, breaks, and unusual activity detected by "
            "the Isolation Forest model."
        )

    return jsonify({
        "success": True,
        "answer": answer
    })