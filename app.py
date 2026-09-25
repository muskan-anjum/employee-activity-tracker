from flask import Flask, redirect, url_for, session, request, jsonify
from flask_login import LoginManager

from config import Config
from models import db, User
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.assistant import assistant_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    from services.security import init_security
    init_security(app)

    # Initialize database
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assistant_bp)

    # Initialize authentication
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        from models import LoginSession
        try:
            user = db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None
        record = db.session.get(LoginSession, session.get("login_session_id")) if session.get("login_session_id") else None
        if not user or not user.is_active_account or not record or record.user_id != user.id or record.logout_time is not None:
            return None
        return user

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.is_json or request.path.endswith("/state"):
            return jsonify(success=False, message="Please log in again."), 401
        return redirect(url_for("auth.login"))

    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))
        

    # Create database tables and apply lightweight migrations
    with app.app_context():
        db.create_all()
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                cols = [r[1] for r in conn.execute(text("PRAGMA table_info(work_sessions)")).fetchall()]
                if "task_id" not in cols:
                    conn.execute(text("ALTER TABLE work_sessions ADD COLUMN task_id INTEGER REFERENCES tasks(id)"))
                    conn.commit()

                act_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(activity_logs)")).fetchall()]
                if "anomaly_reason" not in act_cols:
                    conn.execute(text("ALTER TABLE activity_logs ADD COLUMN anomaly_reason VARCHAR(255)"))
                    conn.commit()
                login_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(login_sessions)")).fetchall()]
                if "last_seen" not in login_cols:
                    conn.execute(text("ALTER TABLE login_sessions ADD COLUMN last_seen DATETIME"))
                    conn.commit()
        except Exception as e:
            app.logger.warning(f"Schema migration note: {e}")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
