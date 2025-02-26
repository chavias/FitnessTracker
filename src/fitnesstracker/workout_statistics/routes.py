from flask import Blueprint, render_template, request, jsonify
import plotly.express as px
import pandas as pd
from flask_login import login_required, current_user
import json
from src.fitnesstracker import db
from src.fitnesstracker.models import Exercise, ExerciseDetails, TrainingSession, Template


workout_statistics = Blueprint('workout_statistics',
                               __name__,
                               url_prefix='/statistics',
                               template_folder='../template',
                               static_folder='static')


@workout_statistics.route('/progression', methods=['GET'])
@login_required  # Added login_required to ensure user is authenticated
def progression():
    """Render the progression page"""
    return render_template('statistics/progression.html')


@workout_statistics.route('/api/progression', methods=['GET'])
@login_required  # Added login_required
def progression_api():
    """Fetch workout progression data and return JSON for Plotly"""
    exercise_name = request.args.get('exercise', '')
    window_size = int(request.args.get('window', 3))  # Get MA window from request, default=3
    
    if not exercise_name:
        return jsonify({"error": "No exercise provided"}), 400
        
    exercises = (
        db.session.query(
            ExerciseDetails.weight,
            ExerciseDetails.repetitions,
            TrainingSession.date
        )
        .join(Exercise, Exercise.id == ExerciseDetails.exercise_id)
        .join(TrainingSession, TrainingSession.id == Exercise.session_id)
        .filter(Exercise.exercise_name == exercise_name)
        .filter(TrainingSession.user_id == current_user.id)  # Filter by current user
        .order_by(TrainingSession.date)
        .all()
    )
    
    if not exercises:
        return jsonify({"error": "No data found for this exercise"}), 404
        
    df = pd.DataFrame(exercises, columns=["Weight", "Repetitions", "Date"])
    df["Date"] = df["Date"].astype(str)
    df["Volume"] = df["Weight"] * df["Repetitions"]
    df["Weight_MA"] = df["Weight"].rolling(window=window_size, min_periods=1).mean()
    df["Repetitions_MA"] = df["Repetitions"].rolling(window=window_size, min_periods=1).mean()
    
    return jsonify(df.to_dict(orient="records"))


@workout_statistics.route('/api/exercises', methods=['GET'])
@login_required  # Added login_required
def get_exercises():
    """Fetch all distinct exercise names from the database for the current user"""
    exercise_names = (
        db.session.query(Exercise.exercise_name)
        .join(TrainingSession, TrainingSession.id == Exercise.session_id)
        .filter(TrainingSession.user_id == current_user.id)  # Filter by current user
        .distinct()
        .all()
    )
    
    return jsonify([name[0] for name in exercise_names])