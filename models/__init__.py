from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.project import Project
from models.task import Task, TaskUpdate
from models.work_session import WorkSession, Break
from models.activity import ActivityLog
from models.login_session import LoginSession
