from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User, LoginSession


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Already logged-in users should not see the login page again
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("dashboard.admin_dashboard"))
        return redirect(url_for("dashboard.employee_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html")

        user = db.session.scalar(
            db.select(User).where(User.email == email)
        )

        if user and user.check_password(password):
            if not user.is_active_account:
                flash("Your account is currently inactive.", "warning")
                return render_template("login.html")

            login_user(user)

            # Create a new login-session record
            login_record = LoginSession(
                user_id=user.id,
                login_time=datetime.utcnow(),
                is_online=True
            )

            db.session.add(login_record)
            db.session.commit()

            # Remember this exact login session
            session["login_session_id"] = login_record.id

            if user.role == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))

            return redirect(url_for("dashboard.employee_dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    login_session_id = session.get("login_session_id")

    if login_session_id:
        login_record = db.session.get(LoginSession, login_session_id)

        if login_record and login_record.logout_time is None:
            logout_time = datetime.utcnow()

            login_record.logout_time = logout_time
            login_record.is_online = False

            duration = logout_time - login_record.login_time
            login_record.duration_seconds = max(
                0,
                int(duration.total_seconds())
            )

            db.session.commit()

    session.pop("login_session_id", None)

    logout_user()

    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))
