from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models.user import User
from models.activity import ActivityLog
from models.work_session import WorkSession
from models.project import Project
from models import db
from services.ml_analyzer import analyze_activity


assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/admin/assistant", methods=["POST"])
@login_required
def admin_assistant():

    # Only admin can use WorkAI Assistant
    if current_user.role != "admin":
        return jsonify({
            "success": False,
            "answer": "You are not authorized to use the WorkAI Assistant."
        }), 403

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or not isinstance(data.get("question", ""), str):
        return jsonify(success=False, answer="Please provide a text question."), 400
    question = (data.get("question") or "").strip().lower()

    if not question:
        return jsonify({
            "success": False,
            "answer": "Please enter a question."
        }), 400

    # Get recent activity data
    recent_logs = (
        ActivityLog.query
        .order_by(ActivityLog.timestamp.desc())
        .limit(100)
        .all()
    )

    # Run existing Isolation Forest ML analysis
    analysis_results = analyze_activity(recent_logs)

    unusual_results = [
        result
        for result in analysis_results
        if result.get("status") == "Unusual"
    ]

    # -------------------------------------------------
    # ANOMALY / UNUSUAL ACTIVITY QUESTION
    # -------------------------------------------------
    if any(word in question for word in [
        "unusual", "anomaly", "anomalies", "alert", "alerts"
    ]):

        if not recent_logs:
            answer = "There are currently no activity records available for analysis."

        elif not unusual_results:
            answer = (
                f"I analyzed {len(recent_logs)} recent activity records. "
                "The Isolation Forest model did not flag any unusual activity patterns."
            )

        else:
            employee_ids = set()

            for result in unusual_results:
                record = result.get("record")
                if record:
                    employee_ids.add(record.employee_id)

            employees = (
                User.query
                .filter(User.id.in_(employee_ids))
                .all()
                if employee_ids else []
            )

            employee_names = ", ".join(
                employee.name for employee in employees
            )

            answer = (
                f"I analyzed {len(recent_logs)} recent activity records. "
                f"The Isolation Forest model flagged "
                f"{len(unusual_results)} activity intervals as unusual."
            )

            if employee_names:
                answer += (
                    f" The model-flagged records involve: "
                    f"{employee_names}."
                )

            answer += (
                " These are statistical activity anomalies and should "
                "not automatically be treated as employee misconduct."
            )

    # -------------------------------------------------
    # IDLE ACTIVITY QUESTION
    # -------------------------------------------------
    elif "idle" in question:

        employee_stats = {}

        for log in recent_logs:
            if log.employee_id not in employee_stats:
                employee_stats[log.employee_id] = {
                    "active": 0,
                    "idle": 0
                }

            employee_stats[log.employee_id]["active"] += (
                log.active_seconds or 0
            )

            employee_stats[log.employee_id]["idle"] += (
                log.idle_seconds or 0
            )

        high_idle_ids = [
            employee_id
            for employee_id, stats in employee_stats.items()
            if stats["idle"] > stats["active"]
        ]

        if not high_idle_ids:
            answer = (
                "Based on the recent monitored activity records, "
                "no employee currently has more idle time than active time."
            )

        else:
            employees = (
                User.query
                .filter(User.id.in_(high_idle_ids))
                .all()
            )

            names = ", ".join(
                employee.name for employee in employees
            )

            answer = (
                "Based on the recent monitored activity sample, "
                f"higher idle activity was detected for: {names}."
            )

        # -------------------------------------------------
    # PROJECT TIME QUESTION
    # -------------------------------------------------
    elif "project" in question:
        
        sessions = WorkSession.query.filter(
            WorkSession.project_id.isnot(None)
        ).all()

        project_totals = {}

        for session in sessions:
            from services.work_summary import calculate_session_work_seconds
            seconds = calculate_session_work_seconds(session)[0]
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
            top_project_id = max(project_totals, key=project_totals.get)

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
    # -------------------------------------------------
    # WORKFORCE SUMMARY QUESTION
    # -------------------------------------------------
    elif any(word in question for word in [
        "summary", "workforce", "performance", "today", "working", "break"
    ]):

        employee_count = (
            User.query
            .filter_by(role="employee")
            .count()
        )

        active_sessions = (
            WorkSession.query
            .filter_by(end_time=None)
            .all()
        )

        working_count = sum(
            1 for session in active_sessions
            if session.status == "Working"
        )

        break_count = sum(
            1 for session in active_sessions
            if session.status == "On Break"
        )

        total_active = sum(
            log.active_seconds or 0
            for log in recent_logs
        )

        total_idle = sum(
            log.idle_seconds or 0
            for log in recent_logs
        )

        monitored_time = total_active + total_idle

        if monitored_time > 0:
            active_percentage = round(
                (total_active / monitored_time) * 100,
                1
            )
        else:
            active_percentage = 0

        answer = (
            f"WorkAI currently has {employee_count} employees. "
            f"{working_count} employee(s) are working and "
            f"{break_count} employee(s) are on break. "
            f"In the latest {len(recent_logs)} monitored activity records, "
            f"active activity represents approximately "
            f"{active_percentage}% of monitored time. "
            f"The Isolation Forest model flagged "
            f"{len(unusual_results)} unusual activity interval(s)."
        )

    # -------------------------------------------------
    # HELP / UNKNOWN QUESTION
    # -------------------------------------------------
    else:

        answer = (
            "I am the WorkAI Insights Assistant. "
            "You can ask me questions such as: "
            "'Summarize workforce performance', "
            "'Who has high idle activity?', "
            "'Show unusual activity', or "
            "'Which project has the most tracked time?'"
        )

    return jsonify({
        "success": True,
        "answer": answer
    })
