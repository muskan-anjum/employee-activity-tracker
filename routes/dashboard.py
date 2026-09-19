from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import User, db
from models.project import Project
from models.task import Task


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
    from models.work_session import WorkSession
    from models.activity import ActivityLog
    from services.work_summary import generate_work_summary

    tasks = Task.query.filter_by(employee_id=current_user.id).all()

    active_session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).order_by(WorkSession.start_time.desc()).first()

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
        "employee_dashboard.html",
        user=current_user,
        tasks=tasks,
        active_session=active_session,
        work_summary=work_summary
    )

@dashboard_bp.route("/employee/work-summary")
@login_required
@role_required("employee")
def employee_work_summary():
    from models.work_session import WorkSession
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
    return render_template(
        "admin_dashboard.html",
        user=current_user
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
        task.progress = int(progress)

    db.session.commit()
    flash("Task updated successfully.", "success")

    return redirect(url_for("dashboard.employee_dashboard"))

@dashboard_bp.route("/employee/work/start", methods=["POST"])
@login_required
@role_required("employee")
def start_work():
    from models.work_session import WorkSession

    existing_session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).first()

    if existing_session:
        flash("A work session is already active.", "warning")
        return redirect(url_for("dashboard.employee_dashboard"))

    session = WorkSession(
        employee_id=current_user.id,
        status="Working"
    )

    db.session.add(session)
    db.session.commit()

    flash("Work session started successfully.", "success")
    return redirect(url_for("dashboard.employee_dashboard"))
@dashboard_bp.route("/admin/activity")
@login_required
@role_required("admin")
def admin_activity():
    return render_template(
        "admin_activity.html",
        user=current_user
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
    return render_template(
        "admin_reports.html",
        user=current_user
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
        }), 400

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
    from models.work_session import WorkSession

    session = WorkSession.query.filter_by(
        employee_id=current_user.id,
        end_time=None
    ).order_by(WorkSession.start_time.desc()).first()

    if not session:
        return jsonify({
            "success": False,
            "message": "No active work session"
        }), 400

    session.end_time = datetime.utcnow()

    if session.start_time:
        session.total_work_seconds = max(
            0,
            int((session.end_time - session.start_time).total_seconds())
        )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Work session ended successfully",
        "total_work_seconds": session.total_work_seconds
    })