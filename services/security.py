import secrets
from flask import abort, request, session


def init_security(app):
    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        return session["csrf_token"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def protect_mutations():
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        data = request.get_json(silent=True)
        supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
        if not supplied and isinstance(data, dict):
            supplied = data.get("csrf_token")
        expected = session.get("csrf_token")
        if not isinstance(supplied, str) or not expected or not secrets.compare_digest(supplied.encode(), expected.encode()):
            abort(400, "Invalid or missing CSRF token. Refresh the page and try again.")

    @app.after_request
    def private_responses(response):
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response
