from flask import Blueprint, jsonify, render_template, request
from fitnesstracker import db
from fitnesstracker.models import Template, TrainingSession
import pandas as pd

main = Blueprint('main',
                 __name__,
                 template_folder='../template',
                 static_folder='static',
                 static_url_path='/main/static', )


@main.route("/home", methods=['GET'])
@main.route("/index", methods=['GET'])
@main.route("/", methods=['GET'])
def homepage():
    page = request.args.get('page', 1, type=int)
    sessions = TrainingSession.query.order_by(TrainingSession.date.desc()).paginate(page=page, per_page=5)
    return render_template("index.html", sessions=sessions)


@main.route('/api/training_sessions', methods=['GET'])
def get_training_sessions():
    """Fetch all training sessions with date and template name"""
    sessions = (
        db.session.query(TrainingSession.date, Template.name, Template.id)
        .join(Template, Template.id == TrainingSession.template_id)
        .order_by(TrainingSession.date)
        .all()
    )

    if not sessions:
        return jsonify({"error": "No training data found"}), 404
    
    df = pd.DataFrame(sessions, columns=["Date", "Template", "Id"])
    df["Date"] = df["Date"].astype(str)  # Ensure date is string format for JSON

    return jsonify(df.to_dict(orient="records"))
