from fastapi import FastAPI
from pydantic import BaseModel, Field
from app import app as flask_app
from models import db, User, Project, Task, WorkSession, ActivityLog
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware


api = FastAPI(
    title="WorkAI Intelligence API",
    description=(
        "Professional analytics and AI service layer for the WorkAI "
        "Workforce Intelligence & Activity Analytics Platform."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://employee-activity-tracker.onrender.com",
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@api.get("/", tags=["System"])
def api_home():
    return {
        "platform": "WorkAI",
        "service": "WorkAI Intelligence API",
        "version": "1.0.0",
        "status": "operational",
    }


@api.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "WorkAI Intelligence API",
        "api_version": "1.0.0",
        "ml_engine": "available",
    }
class ActivityAnalysisRequest(BaseModel):
    active_seconds: int = Field(ge=0, description="Employee active time in seconds")
    idle_seconds: int = Field(ge=0, description="Employee idle time in seconds")
    keyboard_events: int = Field(ge=0, description="Number of keyboard interaction events")
    mouse_events: int = Field(ge=0, description="Number of mouse interaction events")


class ActivityAnalysisResponse(BaseModel):
    activity_score: float
    activity_level: str
    active_percentage: float
    idle_percentage: float
    total_interactions: int
    insight: str


@api.post(
    "/api/activity/analyze",
    response_model=ActivityAnalysisResponse,
    tags=["Activity Intelligence"],
    summary="Analyze employee activity",
)
def analyze_employee_activity(data: ActivityAnalysisRequest):
    total_time = data.active_seconds + data.idle_seconds

    if total_time > 0:
        active_percentage = (data.active_seconds / total_time) * 100
        idle_percentage = (data.idle_seconds / total_time) * 100
    else:
        active_percentage = 0.0
        idle_percentage = 0.0

    total_interactions = data.keyboard_events + data.mouse_events

    activity_score = round(active_percentage, 2)

    if activity_score >= 80:
        activity_level = "Highly Active"
        insight = "Strong activity pattern with high active-time concentration."
    elif activity_score >= 60:
        activity_level = "Active"
        insight = "Healthy activity pattern with moderate idle time."
    elif activity_score >= 40:
        activity_level = "Moderate"
        insight = "Balanced activity pattern with room for improved active-time consistency."
    else:
        activity_level = "Low Activity"
        insight = "Higher idle-time concentration detected for this activity interval."

    return ActivityAnalysisResponse(
        activity_score=activity_score,
        activity_level=activity_level,
        active_percentage=round(active_percentage, 2),
        idle_percentage=round(idle_percentage, 2),
        total_interactions=total_interactions,
        insight=insight,
    )
class MLActivityRequest(BaseModel):
    active_seconds: int = 0
    idle_seconds: int = 0
    keyboard_events: int = 0
    mouse_events: int = 0


@api.post(
    "/api/ml/analyze",
    tags=["AI & Machine Learning"],
    summary="Analyze activity using WorkAI ML engine"
)
def ml_activity_analysis(data: MLActivityRequest):
    from services.ml_analyzer import analyze_activity
    from types import SimpleNamespace

    activity_records = [
        SimpleNamespace(
            active_seconds=data.active_seconds,
            idle_seconds=data.idle_seconds,
            keyboard_events=data.keyboard_events,
            mouse_events=data.mouse_events
        )
    ]

    results = analyze_activity(activity_records)

    return {
        "service": "WorkAI ML Intelligence",
        "engine": "Isolation Forest",
        "features": [
            "active_seconds",
            "idle_seconds",
            "keyboard_events",
            "mouse_events"
        ],
        "analysis": results
    }
@api.get(
    "/api/status",
    tags=["System"],
    summary="Get WorkAI platform status"
)
def platform_status():
    return {
        "platform": "WorkAI",
        "status": "Operational",
        "web_application": "Flask",
        "intelligence_api": "FastAPI",
        "ml_engine": "Isolation Forest",
        "api_version": "1.0.0"
    }

class ProjectAnalyticsRequest(BaseModel):
    project_name: str = Field(min_length=1)
    total_work_seconds: int = Field(ge=0)
    active_seconds: int = Field(ge=0)
    idle_seconds: int = Field(ge=0)
    completed_tasks: int = Field(ge=0)
    total_tasks: int = Field(ge=0)


@api.post(
    "/api/projects/analyze",
    tags=["Project Intelligence"],
    summary="Analyze project productivity"
)
def analyze_project(data: ProjectAnalyticsRequest):
    tracked_seconds = data.active_seconds + data.idle_seconds

    if tracked_seconds > 0:
        activity_score = round(
            (data.active_seconds / tracked_seconds) * 100, 2
        )
    else:
        activity_score = 0.0

    if data.total_tasks > 0:
        completion_rate = round(
            (data.completed_tasks / data.total_tasks) * 100, 2
        )
    else:
        completion_rate = 0.0

    if activity_score >= 80 and completion_rate >= 75:
        health = "Excellent"
        insight = "Strong activity and task completion performance."
    elif activity_score >= 60 and completion_rate >= 50:
        health = "Healthy"
        insight = "Project performance is progressing at a healthy level."
    elif activity_score >= 40:
        health = "Moderate"
        insight = "Project activity is moderate and task progress can be improved."
    else:
        health = "Needs Attention"
        insight = "Lower activity or task completion levels require review."

    return {
        "project": data.project_name,
        "project_health": health,
        "activity_score": activity_score,
        "task_completion_rate": completion_rate,
        "total_work_seconds": data.total_work_seconds,
        "insight": insight
    }

class WorkforceAnalyticsRequest(BaseModel):
    total_employees: int = Field(ge=0)
    active_employees: int = Field(ge=0)
    total_active_seconds: int = Field(ge=0)
    total_idle_seconds: int = Field(ge=0)
    completed_tasks: int = Field(ge=0)
    total_tasks: int = Field(ge=0)


@api.post(
    "/api/workforce/analyze",
    tags=["Workforce Intelligence"],
    summary="Analyze workforce productivity"
)
def analyze_workforce(data: WorkforceAnalyticsRequest):
    tracked_seconds = data.total_active_seconds + data.total_idle_seconds

    if tracked_seconds > 0:
        productivity_score = round(
            (data.total_active_seconds / tracked_seconds) * 100, 2
        )
    else:
        productivity_score = 0.0

    if data.total_employees > 0:
        active_employee_rate = round(
            (data.active_employees / data.total_employees) * 100, 2
        )
    else:
        active_employee_rate = 0.0

    if data.total_tasks > 0:
        task_completion_rate = round(
            (data.completed_tasks / data.total_tasks) * 100, 2
        )
    else:
        task_completion_rate = 0.0

    if productivity_score >= 80:
        workforce_status = "High Productivity"
        insight = "Workforce activity indicates strong productive engagement."
    elif productivity_score >= 60:
        workforce_status = "Healthy"
        insight = "Workforce productivity is operating at a healthy level."
    elif productivity_score >= 40:
        workforce_status = "Moderate"
        insight = "Workforce activity is moderate with opportunities for improvement."
    else:
        workforce_status = "Needs Attention"
        insight = "Workforce activity indicates a higher concentration of idle time."

    return {
        "workforce_status": workforce_status,
        "productivity_score": productivity_score,
        "active_employee_rate": active_employee_rate,
        "task_completion_rate": task_completion_rate,
        "total_employees": data.total_employees,
        "active_employees": data.active_employees,
        "insight": insight
    }

@api.get(
    "/api/workforce/overview",
    tags=["Workforce Intelligence"],
    summary="Get live WorkAI workforce overview"
)
def get_workforce_overview():
    with flask_app.app_context():
        total_employees = User.query.filter_by(role="employee").count()

        active_accounts = User.query.filter_by(
            role="employee",
            is_active_account=True
        ).count()

        active_sessions = (
            db.session.query(
                func.count(func.distinct(WorkSession.employee_id))
            )
            .filter(
                WorkSession.status.in_(["Working", "On Break"])
            )
            .scalar()
            or 0
        )
        total_projects = Project.query.count()

        active_projects = Project.query.filter_by(
            status="Active"
        ).count()

        total_tasks = Task.query.count()

        completed_tasks = Task.query.filter_by(
            status="Completed"
        ).count()

        total_work_seconds = (
            db.session.query(
                func.coalesce(func.sum(WorkSession.total_work_seconds), 0)
            ).scalar()
            or 0
        )

        total_active_seconds = (
            db.session.query(
                func.coalesce(func.sum(ActivityLog.active_seconds), 0)
            ).scalar()
            or 0
        )

        total_idle_seconds = (
            db.session.query(
                func.coalesce(func.sum(ActivityLog.idle_seconds), 0)
            ).scalar()
            or 0
        )

        tracked_seconds = total_active_seconds + total_idle_seconds

        activity_score = (
            round((total_active_seconds / tracked_seconds) * 100, 2)
            if tracked_seconds > 0
            else 0.0
        )

        return {
            "platform": "WorkAI",
            "data_source": "Live WorkAI Database",
            "employees": {
                "total": total_employees,
                "active_accounts": active_accounts,
                "currently_working": active_sessions
            },
            "projects": {
                "total": total_projects,
                "active": active_projects
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks
            },
            "activity": {
                "total_work_seconds": int(total_work_seconds),
                "active_seconds": int(total_active_seconds),
                "idle_seconds": int(total_idle_seconds),
                "activity_score": activity_score
            }
        }

@api.get(
    "/api/projects/overview",
    tags=["Project Intelligence"],
    summary="Get live analytics for all WorkAI projects"
)
def get_projects_overview():
    with flask_app.app_context():
        projects = Project.query.order_by(Project.id.asc()).all()
        project_results = []

        for project in projects:
            tasks = Task.query.filter_by(project_id=project.id).all()

            total_tasks = len(tasks)
            completed_tasks = sum(
                1 for task in tasks
                if task.status.lower() == "completed"
            )

            task_completion_rate = (
                round((completed_tasks / total_tasks) * 100, 2)
                if total_tasks > 0
                else 0.0
            )

            sessions = WorkSession.query.filter_by(
                project_id=project.id
            ).all()

            session_ids = [session.id for session in sessions]

            total_work_seconds = sum(
                session.total_work_seconds or 0
                for session in sessions
            )

            if session_ids:
                activity_totals = (
                    db.session.query(
                        func.coalesce(
                            func.sum(ActivityLog.active_seconds), 0
                        ),
                        func.coalesce(
                            func.sum(ActivityLog.idle_seconds), 0
                        )
                    )
                    .filter(ActivityLog.session_id.in_(session_ids))
                    .first()
                )

                active_seconds = int(activity_totals[0] or 0)
                idle_seconds = int(activity_totals[1] or 0)
            else:
                active_seconds = 0
                idle_seconds = 0

            tracked_seconds = active_seconds + idle_seconds

            activity_score = (
                round((active_seconds / tracked_seconds) * 100, 2)
                if tracked_seconds > 0
                else 0.0
            )

            assigned_employee_ids = {
                task.employee_id for task in tasks
            }

            project_results.append({
                "project_id": project.id,
                "project_name": project.name,
                "status": project.status,
                "assigned_employees": len(assigned_employee_ids),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "task_completion_rate": task_completion_rate,
                "total_work_seconds": total_work_seconds,
                "active_seconds": active_seconds,
                "idle_seconds": idle_seconds,
                "activity_score": activity_score
            })

        return {
            "platform": "WorkAI",
            "data_source": "Live WorkAI Database",
            "total_projects": len(project_results),
            "projects": project_results
        }

@api.get(
    "/api/ml/recent-analysis",
    tags=["AI & Machine Learning"],
    summary="Analyze recent WorkAI activity using the ML engine"
)
def analyze_recent_activity(limit: int = 100):
    from services.ml_analyzer import analyze_activity

    safe_limit = max(5, min(limit, 500))

    with flask_app.app_context():
        logs = (
            ActivityLog.query
            .order_by(ActivityLog.timestamp.desc())
            .limit(safe_limit)
            .all()
        )

        if not logs:
            return {
                "service": "WorkAI ML Intelligence",
                "engine": "Isolation Forest",
                "records_analyzed": 0,
                "message": "No activity records are available for analysis.",
                "analysis": []
            }

        results = analyze_activity(logs)

        unusual_count = sum(
            1 for result in results
            if result.get("status") == "Unusual"
        )

        normal_count = len(results) - unusual_count

        return {
            "service": "WorkAI ML Intelligence",
            "engine": "Isolation Forest",
            "data_source": "Live WorkAI Activity Database",
            "records_analyzed": len(results),
            "normal_patterns": normal_count,
            "unusual_patterns": unusual_count,
            "analysis": results
        }

@api.get(
    "/api/employees/overview",
    tags=["Employee Intelligence"],
    summary="Get live employee analytics from WorkAI"
)
def get_employees_overview():
    with flask_app.app_context():
        employees = User.query.filter_by(role="employee").all()
        employee_results = []

        for employee in employees:
            sessions = WorkSession.query.filter_by(
                employee_id=employee.id
            ).all()

            logs = ActivityLog.query.filter_by(
                employee_id=employee.id
            ).all()

            tasks = Task.query.filter_by(
                employee_id=employee.id
            ).all()

            total_work_seconds = sum(
                session.total_work_seconds or 0
                for session in sessions
            )

            active_seconds = sum(
                log.active_seconds or 0
                for log in logs
            )

            idle_seconds = sum(
                log.idle_seconds or 0
                for log in logs
            )

            tracked_seconds = active_seconds + idle_seconds

            activity_score = (
                round((active_seconds / tracked_seconds) * 100, 2)
                if tracked_seconds > 0
                else 0.0
            )

            total_tasks = len(tasks)

            completed_tasks = sum(
                1 for task in tasks
                if task.status.strip().lower() == "completed"
            )

            task_completion_rate = (
                round((completed_tasks / total_tasks) * 100, 2)
                if total_tasks > 0
                else 0.0
            )

            currently_working = any(
                session.status in ["Working", "On Break"]
                for session in sessions
            )

            employee_results.append({
                "employee_id": employee.id,
                "name": employee.name,
                "account_active": employee.is_active_account,
                "currently_working": currently_working,
                "total_work_seconds": total_work_seconds,
                "active_seconds": active_seconds,
                "idle_seconds": idle_seconds,
                "activity_score": activity_score,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "task_completion_rate": task_completion_rate
            })

        return {
            "platform": "WorkAI",
            "data_source": "Live WorkAI Database",
            "total_employees": len(employee_results),
            "employees": employee_results
        }

@api.get(
    "/api/workforce/overview",
    tags=["Workforce Intelligence"],
    summary="Get live workforce intelligence from WorkAI"
)
def get_workforce_overview():
    with flask_app.app_context():

        employees = User.query.filter_by(role="employee").all()
        sessions = WorkSession.query.all()
        logs = ActivityLog.query.all()
        tasks = Task.query.all()

        total_employees = len(employees)

        active_accounts = sum(
            1 for employee in employees
            if employee.is_active_account
        )

        currently_working = sum(
            1 for session in sessions
            if session.status in ["Working", "On Break"]
        )

        total_work_seconds = sum(
            session.total_work_seconds or 0
            for session in sessions
        )

        active_seconds = sum(
            log.active_seconds or 0
            for log in logs
        )

        idle_seconds = sum(
            log.idle_seconds or 0
            for log in logs
        )

        tracked_seconds = active_seconds + idle_seconds

        workforce_activity_score = (
            round((active_seconds / tracked_seconds) * 100, 2)
            if tracked_seconds > 0
            else 0.0
        )

        total_tasks = len(tasks)

        completed_tasks = sum(
            1 for task in tasks
            if task.status.strip().lower() == "completed"
        )

        task_completion_rate = (
            round((completed_tasks / total_tasks) * 100, 2)
            if total_tasks > 0
            else 0.0
        )

        if workforce_activity_score >= 80:
            workforce_status = "High Productivity"
        elif workforce_activity_score >= 60:
            workforce_status = "Stable Productivity"
        else:
            workforce_status = "Needs Attention"

        return {
            "platform": "WorkAI",
            "data_source": "Live WorkAI Database",
            "workforce_status": workforce_status,
            "total_employees": total_employees,
            "active_accounts": active_accounts,
            "currently_working": currently_working,
            "total_work_seconds": total_work_seconds,
            "active_seconds": active_seconds,
            "idle_seconds": idle_seconds,
            "workforce_activity_score": workforce_activity_score,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "task_completion_rate": task_completion_rate
        }

# Serve the existing Flask WorkAI web application through FastAPI.
# Keep this mount LAST so /api, /docs and /redoc remain handled by FastAPI.
api.mount("/", WSGIMiddleware(flask_app))