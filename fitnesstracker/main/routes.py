from flask import Blueprint, render_template, request
from fitnesstracker.models import TrainingSession

main = Blueprint('main', __name__)


@main.route("/home")
@main.route("/")
def homepage():
    page = request.args.get('page', 1, type=int)
    sessions = TrainingSession.query.order_by(TrainingSession.date.desc()).paginate(page=page, per_page=5)
    return render_template("index.html", sessions=sessions)
