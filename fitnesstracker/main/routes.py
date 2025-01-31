from flask import Blueprint, render_template
from fitnesstracker.models import TrainingSession


main = Blueprint('main', __name__)


@main.route("/home")
@main.route("/")
def homepage():
    sessions = TrainingSession.query.order_by(TrainingSession.id.desc()).all()
    return render_template("index.html", sessions=sessions)
