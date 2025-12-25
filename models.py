from . import db
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(500),nullable=False)


class TaskDoneToday(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Optional references so we don’t break history when user/task is deleted
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True
    )
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id', ondelete='SET NULL'),
        nullable=True
    )

    # Keep a snapshot of the info in case the parent is deleted
    username = db.Column(db.String(150), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    task_category = db.Column(db.String(100), nullable=False)
    task_method = db.Column(db.String(500),nullable=False)

    date = db.Column(db.Date, default=date.today, nullable=False)

    user = db.relationship('User', backref=db.backref('tasks_done_today', lazy='dynamic'))
    task = db.relationship('Task', backref=db.backref('tasks_done_today', lazy='dynamic'))


class TaskHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True
    )
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('task.id', ondelete='SET NULL'),
        nullable=True
    )

    # Keep snapshots of fields
    username = db.Column(db.String(150), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    task_category = db.Column(db.String(100), nullable=False)
    method_at_completion = db.Column(db.String(500),nullable=False)
    comment = db.Column(db.Text, nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    points_at_completion = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('task_histories', lazy='dynamic'))
    task = db.relationship('Task', backref=db.backref('task_histories', lazy='dynamic'))
