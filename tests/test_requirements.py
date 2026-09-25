"""Run with: python -m unittest discover -s tests -v (isolated SQLite database)."""
import os
os.environ["DATABASE_URL"] = "sqlite://"

import csv
import io
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from app import create_app
from models import db, User, Project, Task, TaskUpdate, WorkSession, Break, ActivityLog, LoginSession
from services.work_summary import calculate_session_work_seconds, generate_work_summary
from services.ml_analyzer import analyze_activity


class RequirementsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SECRET_KEY": "test-only"})
        with self.app.app_context():
            for name, role in [("Admin", "admin"), ("Alice", "employee"), ("Bob", "employee")]:
                user = User(name=name, email=f"{name.lower()}@example.com", role=role)
                user.set_password("test-password")
                db.session.add(user)
            db.session.flush()
            project = Project(name="Assigned project")
            other = Project(name="Other project")
            db.session.add_all([project, other]); db.session.flush()
            db.session.add_all([Task(title="Alice task", employee_id=2, project_id=project.id),
                                Task(title="Bob task", employee_id=3, project_id=other.id)])
            db.session.commit()
        self.employee = self.app.test_client()
        self.admin = self.app.test_client()
        self.login(self.employee, "alice")
        self.login(self.admin, "admin")

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def token(self, client):
        with client.session_transaction() as cookie:
            return cookie["csrf_token"]

    def post(self, client, path, **kwargs):
        return client.post(path, headers={"X-CSRF-Token": self.token(client)}, **kwargs)

    def login(self, client, name, password="test-password"):
        client.get("/login")
        return self.post(client, "/login", data={"email": f"{name}@example.com", "password": password})

    def start(self):
        response = self.post(self.employee, "/employee/work/start", json={"task_id": 1})
        self.assertEqual(response.status_code, 200)
        return response.json["session_id"]

    def test_role_boundaries_and_csrf(self):
        self.assertEqual(self.employee.get("/admin/dashboard").status_code, 403)
        self.assertEqual(self.admin.get("/employee/dashboard").status_code, 403)
        self.assertEqual(self.employee.post("/employee/work/start", json={}).status_code, 400)
        self.assertEqual(self.app.test_client().get("/employee/work/state").status_code, 401)
        self.assertEqual(self.employee.get("/logout").status_code, 405)

    def test_assignment_and_project_validation(self):
        for body, code in [({"task_id": 2}, 403), ({"project_id": 2}, 403),
                           ({"task_id": 1, "project_id": 2}, 400), ([1], 400),
                           ({"task_id": "bad"}, 400)]:
            self.assertEqual(self.post(self.employee, "/employee/work/start", json=body).status_code, code)
        with self.app.app_context():
            db.session.get(Project, 1).status = "Completed"; db.session.commit()
        self.assertEqual(self.post(self.employee, "/employee/work/start", json={"task_id": 1}).status_code, 400)

    def test_work_break_resume_end_and_net_time(self):
        sid = self.start()
        self.assertEqual(self.post(self.employee, "/employee/work/start", json={}).status_code, 400)
        with self.app.app_context():
            db.session.get(WorkSession, sid).start_time = datetime.utcnow() - timedelta(hours=1)
            db.session.commit()
        self.assertEqual(self.post(self.employee, "/employee/work/break").status_code, 200)
        self.assertEqual(self.post(self.employee, "/employee/work/break").status_code, 400)
        with self.app.app_context():
            Break.query.one().start_time = datetime.utcnow() - timedelta(minutes=10)
            db.session.commit()
        paused = self.employee.get("/employee/work/state").json
        self.assertEqual(paused["status"], "On Break")
        self.assertAlmostEqual(paused["net_seconds"], 3000, delta=2)
        self.assertEqual(self.post(self.employee, "/employee/work/end-break").status_code, 200)
        self.assertEqual(self.post(self.employee, "/employee/work/end-break").status_code, 400)
        ended = self.post(self.employee, "/employee/end-work").json
        self.assertAlmostEqual(ended["total_work_seconds"], 3000, delta=2)
        self.assertEqual(self.employee.get("/employee/work/state").json["status"], "Stopped")

    def test_deactivation_revokes_all_logins_and_closes_break(self):
        second = self.app.test_client(); self.login(second, "alice")
        sid = self.start()
        with self.app.app_context():
            db.session.get(WorkSession, sid).start_time = datetime.utcnow() - timedelta(minutes=20)
            db.session.add(Break(session_id=sid, start_time=datetime.utcnow() - timedelta(minutes=5)))
            db.session.commit()
        self.post(self.admin, "/admin/employees/2/toggle-status")
        for client in [self.employee, second]:
            self.assertEqual(client.get("/employee/work/state").status_code, 401)
        with self.app.app_context():
            work = db.session.get(WorkSession, sid)
            self.assertEqual(work.status, "Terminated")
            self.assertAlmostEqual(work.total_work_seconds, 900, delta=2)
            self.assertIsNotNone(work.breaks[0].end_time)
            self.assertEqual(LoginSession.query.filter_by(user_id=2, logout_time=None).count(), 0)
        self.post(self.admin, "/admin/employees/2/toggle-status")
        self.assertEqual(second.get("/employee/work/state").status_code, 401)

    def test_password_reset_invalidates_existing_session(self):
        self.post(self.admin, "/admin/employees/2/reset-password", data={"new_password": "replacement-pass"})
        self.assertEqual(self.employee.get("/employee/work/state").status_code, 401)
        self.login(self.employee, "alice", "replacement-pass")
        self.assertEqual(self.employee.get("/employee/work/state").status_code, 200)

    def test_presence_expires_without_heartbeat(self):
        self.start()
        with self.app.app_context():
            LoginSession.query.filter_by(user_id=2).one().last_seen = datetime.utcnow()-timedelta(minutes=5)
            db.session.commit()
        self.assertFalse(self.admin.get("/admin/live").json["employees"][0]["online"])
        self.employee.get("/employee/work/state")
        self.assertTrue(self.admin.get("/admin/live").json["employees"][0]["online"])

    def test_telemetry_privacy_validation_and_break_suppression(self):
        sid = self.start()
        body = dict(session_id=sid, active_seconds=20, idle_seconds=10, keyboard_events=8, mouse_events=4)
        self.assertEqual(self.post(self.employee, "/employee/activity", json=body).status_code, 201)
        for value in [-1, 1.5, True, "12", None, 100000000000]:
            self.assertEqual(self.post(self.employee, "/employee/activity", json={**body, "active_seconds": value}).status_code, 400)
        self.assertEqual(self.post(self.employee, "/employee/activity", json={**body, "session_id": sid + 1}).status_code, 409)
        self.post(self.employee, "/employee/work/break")
        self.assertFalse(self.post(self.employee, "/employee/activity", json=body).json["success"])
        with self.app.app_context():
            self.assertEqual(ActivityLog.query.count(), 1)
            self.assertNotIn("keys", ActivityLog.__table__.columns.keys())

    def test_overnight_work_and_breaks_are_clipped_to_report_window(self):
        start = datetime(2026, 9, 24)
        work = SimpleNamespace(start_time=start-timedelta(hours=2), end_time=start+timedelta(hours=2),
                               breaks=[SimpleNamespace(start_time=start-timedelta(minutes=15), end_time=start+timedelta(minutes=15))])
        self.assertEqual(calculate_session_work_seconds(work, start, start+timedelta(days=1)), (6300, 900))
        self.assertEqual(calculate_session_work_seconds(work, start+timedelta(days=1), start+timedelta(days=2)), (0, 0))

    def test_historical_summary_and_report_csv_agree(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        with self.app.app_context():
            work = WorkSession(employee_id=2, start_time=today-timedelta(hours=2), end_time=today+timedelta(minutes=10), status="Completed")
            db.session.add(work); db.session.commit()
        fixed_now = today + timedelta(hours=12)
        class FrozenDatetime(datetime):
            @classmethod
            def utcnow(cls):
                return fixed_now
        with patch("datetime.datetime", FrozenDatetime):
            response = self.admin.get("/admin/reports/export?period=daily")
        self.assertEqual(response.status_code, 200)
        rows = list(csv.DictReader(io.StringIO(response.text)))
        self.assertEqual(next(row for row in rows if row["Employee"] == "Alice")["Net Work Time"], "00:10:00")
        historical = self.employee.get("/employee/work-summary?date=" + (today-timedelta(days=1)).date().isoformat())
        self.assertEqual(historical.status_code, 200)
        self.assertIn("02:00:00", historical.text)
        self.assertEqual(self.employee.get("/employee/work-summary?date=bad").status_code, 400)

    def test_management_and_task_updates(self):
        self.post(self.admin, "/admin/employees", data={"name": "New", "email": "new@example.com", "password": "new-password"})
        self.post(self.admin, "/admin/projects", data={"name": "New project"})
        self.post(self.admin, "/admin/tasks", data={"title": "New assignment", "project_id": 3, "employee_id": 4})
        self.assertEqual(self.post(self.employee, "/employee/task/1/update", data={"status": "Bogus"}).status_code, 400)
        self.post(self.employee, "/employee/task/1/update", data={"status": "Completed", "progress": "100"})
        with self.app.app_context():
            self.assertEqual(db.session.get(Task, 1).progress, 100)
            self.assertEqual(Task.query.filter_by(employee_id=4).count(), 1)

    def test_all_pages_render_and_live_data_is_scoped(self):
        self.start()
        for path in ["dashboard", "projects", "activity-history", "work-summary"]:
            self.assertEqual(self.employee.get("/employee/"+path).status_code, 200, path)
        for path in ["dashboard", "employees", "projects", "activity", "ai-analysis", "reports", "login-sessions"]:
            self.assertEqual(self.admin.get("/admin/"+path).status_code, 200, path)
        for period in ["daily", "weekly", "monthly"]:
            self.assertEqual(self.admin.get("/admin/reports?period="+period).status_code, 200)
            self.assertEqual(self.admin.get("/admin/reports/export?period="+period).status_code, 200)
        live = self.admin.get("/admin/live").json
        self.assertEqual(live["employees"][0]["name"], "Alice")
        self.assertEqual(self.employee.get("/admin/live").status_code, 403)
        self.assertIn("Alice task", self.employee.get("/employee/activity-history").text)
        self.assertNotIn("Alice task", self.admin.get("/admin/activity?employee_id=3").text)
        answer = self.post(self.admin, "/admin/assistant", json={"question": "Who is working?"})
        self.assertEqual(answer.status_code, 200)

    def test_isolation_forest_and_cold_start_explanations(self):
        records = [SimpleNamespace(active_seconds=25, idle_seconds=5, keyboard_events=30+i, mouse_events=20+i) for i in range(25)]
        outlier = SimpleNamespace(active_seconds=1, idle_seconds=29, keyboard_events=20000, mouse_events=0)
        results = analyze_activity(records+[outlier])
        self.assertTrue(results[-1]["is_anomaly"])
        self.assertTrue(all(r["reason"] for r in results))
        self.assertEqual(len(analyze_activity([outlier])), 1)

    def test_task_milestones_survive_later_edits(self):
        self.post(self.employee, "/employee/task/1/update", data={"progress": 100})
        with self.app.app_context():
            yesterday = datetime.utcnow()-timedelta(days=1)
            TaskUpdate.query.one().timestamp = yesterday
            db.session.commit()
        self.post(self.employee, "/employee/task/1/update", data={"progress": 25})
        response = self.employee.get("/employee/work-summary?date=" + yesterday.date().isoformat())
        self.assertIn("Alice task: Completed (100%)", response.text)

    def test_logout_audit_and_csv_formula_escaping(self):
        with self.app.app_context():
            db.session.get(User, 2).name = "=SUM(1,2)"
            db.session.commit()
        rows = list(csv.DictReader(io.StringIO(self.admin.get("/admin/reports/export").text)))
        self.assertTrue(rows[0]["Employee"].startswith("'="))
        self.post(self.employee, "/logout")
        self.assertEqual(self.employee.get("/employee/work/state").status_code, 401)
        with self.app.app_context():
            record = LoginSession.query.filter_by(user_id=2).one()
            self.assertIsNotNone(record.logout_time)
            self.assertFalse(record.is_online)

    def test_analytics_api_rejects_unauthorized_access(self):
        import asyncio
        import base64
        import fastapi_app

        async def get(path, username=None):
            messages = []
            headers = []
            if username:
                token = base64.b64encode(f"{username}@example.com:test-password".encode())
                headers = [(b"authorization", b"Basic " + token)]
            scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "GET",
                     "scheme": "http", "path": path, "raw_path": path.encode(), "query_string": b"",
                     "root_path": "", "headers": headers, "server": ("test", 80), "client": ("test", 1)}
            async def receive():
                return {"type": "http.request", "body": b"", "more_body": False}
            async def send(message):
                messages.append(message)
            await fastapi_app.api(scope, receive, send)
            return next(m["status"] for m in messages if m["type"] == "http.response.start")

        with patch.object(fastapi_app, "flask_app", self.app):
            self.assertEqual(asyncio.run(get("/health")), 200)
            self.assertEqual(asyncio.run(get("/api/workforce/overview")), 401)
            self.assertEqual(asyncio.run(get("/api/workforce/overview", "alice")), 401)
            for path in ["/api/workforce/overview", "/api/projects/overview", "/api/employees/overview", "/api/ml/recent-analysis"]:
                self.assertEqual(asyncio.run(get(path, "admin")), 200)


if __name__ == "__main__":
    unittest.main()
