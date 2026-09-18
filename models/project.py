from models import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="Active")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
    )

    def __repr__(self):
        return f"<Project {self.name}>"