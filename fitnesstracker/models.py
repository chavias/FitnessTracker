from fitnesstracker import db
from datetime import datetime


# Database Models
class Template(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exercises = db.relationship("TemplateExercise", backref="template", cascade="all, delete-orphan", lazy=True)
    sessions = db.relationship('TrainingSession', backref='template', lazy=True)

class TemplateExercise(db.Model):
    __tablename__ = "template_exercises"
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey("templates.id"), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)


class TrainingSession(db.Model):
    __tablename__ = 'training_sessions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'))
    exercises = db.relationship('Exercise', backref='session', lazy=True)


class Exercise(db.Model):
    __tablename__ = 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    # sets = db.Column(db.Integer, nullable=False)
    # reps = db.Column(db.Integer, nullable=False)
    # weight = db.Column(db.Float, nullable=False)
    details = db.relationship('ExerciseDetails', backref='exercise', lazy=True)


class ExerciseDetails(db.Model):
    __tablename__ = 'exercise_details'
    id = db.Column(db.Integer, primary_key=True)
    repetitions = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
