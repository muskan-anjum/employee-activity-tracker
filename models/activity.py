from models import db


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("work_sessions.id"),
        nullable=False,
        index=True
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True
    )

    active_seconds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    idle_seconds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    keyboard_events = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    mouse_events = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    is_anomaly = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    anomaly_score = db.Column(
        db.Float,
        nullable=True
    )

    anomaly_reason = db.Column(
        db.String(255),
        nullable=True
    )

    employee = db.relationship(
        "User",
        backref=db.backref("activity_logs", lazy=True)
    )

    session = db.relationship(
        "WorkSession",
        backref=db.backref(
            "activity_logs",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )