from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
from models import db, User
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Initialize authentication
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))
        

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)