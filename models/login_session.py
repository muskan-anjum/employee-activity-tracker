from models import db
from datetime import datetime


class LoginSession(db.Model):
    __tablename__ = "login_sessions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    login_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    logout_time = db.Column(
        db.DateTime,
        nullable=True
    )

    duration_seconds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_online = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    user = db.relationship(
        "User",
        backref=db.backref("login_sessions", lazy=True)
    )

    def __repr__(self):
        return f"<LoginSession user_id={self.user_id} login_time={self.login_time}>"