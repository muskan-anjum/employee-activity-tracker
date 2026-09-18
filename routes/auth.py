from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User


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

            if user.role == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))

            return redirect(url_for("dashboard.employee_dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))