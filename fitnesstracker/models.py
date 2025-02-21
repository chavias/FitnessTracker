from fitnesstracker import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    templates = db.relationship("Template", backref="user", lazy=True)
    training_sessions = db.relationship("TrainingSession", backref="user", lazy=True)

class Template(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercises = db.relationship("TemplateExercise", backref="template", cascade="all, delete-orphan", lazy=True)
    sessions = db.relationship('TrainingSession', backref='template', cascade='all, delete-orphan', lazy=True)

class TemplateExercise(db.Model):
    __tablename__ = "template_exercises"
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("templates.id"), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)

class TrainingSession(db.Model):
    __tablename__ = 'training_sessions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    exercises = db.relationship('Exercise', backref='session', cascade='all, delete-orphan', lazy=True)

class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    details = db.relationship('ExerciseDetails', backref='exercise', cascade='all, delete-orphan', lazy=True)

class ExerciseDetails(db.Model):
    __tablename__ = 'exercise_details'
    id = db.Column(db.Integer, primary_key=True)
    repetitions = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
