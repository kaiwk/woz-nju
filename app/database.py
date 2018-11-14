import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .utils import TaskType

db = SQLAlchemy()
migrate = Migrate()


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    selected = db.Column(db.Boolean, default=False)
    finished = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.utcnow)
    priority = db.Column(db.Integer, default=0)
    evaluate = db.Column(db.Integer, default=8)
    task_type = db.Column(db.Enum(TaskType), nullable=False)

    def __repr__(self):
        return '<Task {}, finished:{}>'.format(self.id, self.finished)


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
