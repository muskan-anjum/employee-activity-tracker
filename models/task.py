from models import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    status = db.Column(db.String(30), nullable=False, default="Pending")
    progress = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    project = db.relationship(
        "Project",
        backref=db.backref("tasks", lazy=True)
    )

    employee = db.relationship(
        "User",
        backref=db.backref("tasks", lazy=True)
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class TaskUpdate(db.Model):
    """Immutable task snapshots for daily summaries and milestone history."""
    __tablename__ = "task_updates"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    task = db.relationship("Task", backref=db.backref("updates", lazy=True))
    employee = db.relationship("User", backref=db.backref("task_updates", lazy=True))
