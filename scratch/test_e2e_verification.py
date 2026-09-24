import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models import db
from models.user import User
from models.project import Project
from models.task import Task
from models.work_session import WorkSession, Break
from models.activity import ActivityLog
from types import SimpleNamespace
from services.ml_analyzer import analyze_activity, evaluate_single_heuristic
from services.work_summary import generate_work_summary, calculate_session_work_seconds
from datetime import datetime, timedelta

def run_tests():
    print("=" * 60)
    print("🚀 STARTING E2E VERIFICATION OF WORKAI PLATFORM")
    print("=" * 60)
    
    app = create_app()
    client = app.test_client()
    
    with app.app_context():
        # 1. DB Models & Users Check
        admin = User.query.filter_by(email="admin@workai.com").first()
        emp = User.query.filter_by(email="employee@workai.com").first()
        assert admin is not None, "Admin user missing!"
        assert emp is not None, "Employee user missing!"
        print(f"✓ Users verified: Admin ({admin.email}), Employee ({emp.email})")

        # 2. Schema check (task_id and anomaly_reason)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        ws_cols = [c["name"] for c in inspector.get_columns("work_sessions")]
        al_cols = [c["name"] for c in inspector.get_columns("activity_logs")]
        assert "task_id" in ws_cols, "task_id column missing from work_sessions!"
        assert "anomaly_reason" in al_cols, "anomaly_reason column missing from activity_logs!"
        print("✓ Database schema verified: work_sessions.task_id and activity_logs.anomaly_reason present")

        # 3. Work Summary Break Calculation Engine Check
        start_t = datetime.utcnow() - timedelta(hours=2)
        end_t = datetime.utcnow()
        ws_test = WorkSession(employee_id=emp.id, start_time=start_t, end_time=end_t)
        db.session.add(ws_test)
        db.session.flush()

        # Add 30-minute break
        brk = Break(
            session_id=ws_test.id,
            start_time=start_t + timedelta(minutes=15),
            end_time=start_t + timedelta(minutes=45),
            duration_seconds=1800
        )
        db.session.add(brk)
        db.session.commit()

        net_sec, break_sec = calculate_session_work_seconds(ws_test)
        expected_sec = int((end_t - start_t).total_seconds()) - 1800
        assert abs(net_sec - expected_sec) <= 2, f"Break subtraction calculation failed! Got {net_sec}, expected {expected_sec}"
        assert abs(break_sec - 1800) <= 2, f"Break duration calculation failed! Got {break_sec}, expected 1800"
        print(f"✓ Work summary calculation verified: 2h session with 30m break = {net_sec} net work seconds, {break_sec} break seconds")

        # Clean up test session (cascade automatically deletes associated breaks)
        db.session.delete(ws_test)
        db.session.commit()

        # 4. Explainable AI & ML Anomaly Detection Check
        # Normal activity interval
        rec_norm = SimpleNamespace(active_seconds=50, idle_seconds=10, keyboard_events=45, mouse_events=120)
        normal_eval = evaluate_single_heuristic(rec_norm)
        assert not normal_eval["is_anomaly"], "Normal activity falsely flagged as anomaly!"
        print(f"✓ Normal telemetry evaluated: is_anomaly={normal_eval['is_anomaly']}, score={normal_eval['anomaly_score']}")

        # Suspicious activity interval (extreme idle time, zero input events)
        rec_susp = SimpleNamespace(active_seconds=2, idle_seconds=58, keyboard_events=0, mouse_events=0)
        anom_eval = evaluate_single_heuristic(rec_susp)
        assert anom_eval["is_anomaly"], "Suspicious high-idle interval was not flagged as anomaly!"
        assert anom_eval["reason"], "Anomaly reason was empty!"
        print(f"✓ Anomaly correctly flagged: score={anom_eval['anomaly_score']}, reason='{anom_eval['reason']}'")

    # 5. Flask Route Endpoints Authentication & Status Codes
    # Login Employee
    res_login = client.post("/login", data={"email": "employee@workai.com", "password": "Employee@123"}, follow_redirects=True)
    assert res_login.status_code == 200, f"Employee login failed with status {res_login.status_code}"
    print("✓ Employee login successful and redirected to dashboard")

    # Access Employee routes
    for emp_url in ["/employee/dashboard", "/employee/projects", "/employee/activity-history", "/employee/work-summary"]:
        r_emp = client.get(emp_url)
        assert r_emp.status_code == 200, f"Employee route {emp_url} failed with {r_emp.status_code}"
    print("✓ All 4 Employee console views verified (200 OK)")

    # Logout
    client.get("/logout", follow_redirects=True)

    # Login Admin
    res_admin = client.post("/login", data={"email": "admin@workai.com", "password": "Admin@123"}, follow_redirects=True)
    assert res_admin.status_code == 200, f"Admin login failed with status {res_admin.status_code}"
    print("✓ Admin login successful")

    # Admin routes
    for endpoint in ["/admin/dashboard", "/admin/employees", "/admin/projects", "/admin/activity", "/admin/ai-analysis", "/admin/reports", "/admin/login-sessions"]:
        r = client.get(endpoint)
        assert r.status_code == 200, f"Admin endpoint {endpoint} failed with {r.status_code}"
    print("✓ All 7 Admin console views verified (200 OK)")

    # Admin Report Periods & CSV Export
    r_daily = client.get("/admin/reports?period=daily")
    assert r_daily.status_code == 200
    r_weekly = client.get("/admin/reports?period=weekly")
    assert r_weekly.status_code == 200
    r_monthly = client.get("/admin/reports?period=monthly")
    assert r_monthly.status_code == 200
    
    r_csv = client.get("/admin/reports/export?period=weekly")
    assert r_csv.status_code == 200
    assert r_csv.headers.get("Content-Type", "").startswith("text/csv")
    assert "Employee,Email,Period,Net Work Time" in r_csv.data.decode("utf-8")
    print("✓ Multi-period reports (daily, weekly, monthly) and rich CSV export verified")

    # Admin AI Assistant
    r_ai = client.post("/admin/assistant", json={"question": "Who worked the most hours?"})
    assert r_ai.status_code == 200
    json_ai = r_ai.get_json()
    assert "answer" in json_ai
    print(f"✓ WorkAI Assistant chat verified: response received ('{json_ai['answer'][:40]}...')")

    # 6. FastAPI Routes Check
    from fastapi_app import health_check, get_workforce_overview, ml_activity_analysis, MLActivityRequest

    r_health = health_check()
    assert r_health["status"] == "healthy"
    print("✓ FastAPI /health verified (200 OK)")

    r_overview = get_workforce_overview()
    assert "employees" in r_overview
    print(f"✓ FastAPI /api/workforce/overview verified: workforce_status={r_overview['workforce_status']}, employees={r_overview['employees']}")

    ml_req = MLActivityRequest(
        active_seconds=55,
        idle_seconds=5,
        keyboard_events=80,
        mouse_events=40
    )
    ml_res = ml_activity_analysis(ml_req)
    assert "analysis" in ml_res
    first_res = ml_res["analysis"][0]
    print(f"✓ FastAPI /api/ml/analyze verified: status={first_res['status']}, score={first_res['anomaly_score']}")

    print("=" * 60)
    print("🎉 ALL 10 REQUIREMENTS & ARCHITECTURE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
