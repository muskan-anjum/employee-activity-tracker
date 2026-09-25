from models import db


class WorkSession(db.Model):
    __tablename__ = "work_sessions"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=True
    )

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id"),
        nullable=True
    )

    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True
    )

    end_time = db.Column(db.DateTime, nullable=True)

    total_work_seconds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Working"
    )

    employee = db.relationship(
        "User",
        backref=db.backref("work_sessions", lazy=True)
    )

    project = db.relationship(
        "Project",
        backref=db.backref("work_sessions", lazy=True)
    )

    task = db.relationship(
        "Task",
        backref=db.backref("work_sessions", lazy=True)
    )


class Break(db.Model):
    __tablename__ = "breaks"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("work_sessions.id"),
        nullable=False
    )

    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
    )

    end_time = db.Column(db.DateTime, nullable=True)

    duration_seconds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    session = db.relationship(
        "WorkSession",
        backref=db.backref(
            "breaks",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )