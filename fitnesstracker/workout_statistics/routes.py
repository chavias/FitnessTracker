from flask import Blueprint, render_template, request, jsonify
import plotly.express as px
import pandas as pd
import json
from fitnesstracker import db
from fitnesstracker.models import Exercise, ExerciseDetails, TrainingSession

statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

@statistics_bp.route('/progression', methods=['GET'])
def progression():
    """Render the progression page"""
    return render_template('statistics/progression.html')


@statistics_bp.route('/api/progression', methods=['GET'])
def progression_api():
    """Fetch workout progression data and return JSON for Plotly"""
    exercise_name = request.args.get('exercise', '')

    if not exercise_name:
        return jsonify({"error": "No exercise provided"}), 400

    # Efficient query to fetch relevant exercise details with session dates
    exercises = (
        db.session.query(
            ExerciseDetails.weight,
            ExerciseDetails.repetitions,
            TrainingSession.date
        )
        .join(Exercise, Exercise.id == ExerciseDetails.exercise_id)
        .join(TrainingSession, TrainingSession.id == Exercise.session_id)
        .filter(Exercise.exercise_name == exercise_name)
        .order_by(TrainingSession.date)
        .all()
    )

    # If no data, return a 404 error
    if not exercises:
        return jsonify({"error": "No data found"}), 404

    # Convert results into a Pandas DataFrame
    df = pd.DataFrame(exercises, columns=["Weight", "Repetitions", "Date"])
    df["Date"] = df["Date"].astype(str)  # Convert datetime to string for JSON serialization

    return jsonify(df.to_dict(orient="records"))


@statistics_bp.route('/api/exercises', methods=['GET'])
def get_exercises():
    """Fetch all distinct exercise names from the database"""
    exercise_names = db.session.query(Exercise.exercise_name).distinct().all()

    # Flatten list and return JSON response
    return jsonify([name[0] for name in exercise_names])
