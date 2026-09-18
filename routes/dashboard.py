from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request
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
    tasks = Task.query.filter_by(employee_id=current_user.id).all()

    return render_template(
        "employee_dashboard.html",
        user=current_user,
        tasks=tasks
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