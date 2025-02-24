from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from fitnesstracker import db
from flask_login import login_required, current_user
from fitnesstracker.models import Template, TrainingSession
import pandas as pd
from datetime import datetime


main = Blueprint('main',
                 __name__,
                 template_folder='../template',
                 static_folder='static',
                 static_url_path='/main/static', )


@main.route("/home", methods=['GET'])
@main.route("/index", methods=['GET'])
@main.route("/", methods=['GET'])
def homepage():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    page = request.args.get('page', 1, type=int)
    
    # Filter by current user
    sessions = TrainingSession.query\
        .filter_by(user_id=current_user.id)\
        .order_by(TrainingSession.date.desc())\
        .paginate(page=page, per_page=5)
    
    return render_template("index.html", sessions=sessions)

@main.route('/api/training_sessions', methods=['GET'])
@login_required
def get_training_sessions():
    """Fetch all training sessions with date and template name for the current user"""
    sessions = (
        db.session.query(TrainingSession.date, TrainingSession.id, Template.name, Template.id)
        .join(Template, Template.id == TrainingSession.template_id)
        .filter(TrainingSession.user_id == current_user.id)  # Filter by current user
        .order_by(TrainingSession.date)
        .all()
    )
    
    if not sessions:
        return jsonify({"error": "No training data found for your account"}), 404
    
    df = pd.DataFrame(sessions, columns=["Date", "SessionId", "Template", "Id"])
    df["Date"] = df["Date"].apply(lambda x: x.isoformat() if isinstance(x, datetime) else str(x))
    
    return jsonify(df.to_dict(orient="records"))