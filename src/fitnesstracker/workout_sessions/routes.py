from flask import render_template, redirect, jsonify, flash, url_for, Blueprint, abort
from flask_login import current_user, login_required
from fitnesstracker import db
from fitnesstracker.models import Exercise, ExerciseDetails, Template, TrainingSession
from fitnesstracker.workout_sessions.forms import SessionForm
from flask_wtf.csrf import generate_csrf


workout_sessions = Blueprint(
    "workout_sessions",
    __name__,
    static_folder="static",
    static_url_path="/workout_sessions/static",
    template_folder="../templates",
)

@workout_sessions.route("/create_session", methods=["GET", "POST"])
@login_required
def create_session():
    form = SessionForm()
    form.template_id.choices = [(t.id, t.name) for t in Template.query.all()]

    if form.validate_on_submit():
        create_session = TrainingSession(
            template_id=form.template_id.data, date=form.date.data, user_id=current_user.id
        )
        db.session.add(create_session)

        for exercise_form in form.exercises:
            new_exercise = Exercise(
                exercise_name=exercise_form.data["exercise_name"],
                session=create_session,
            )
            db.session.add(new_exercise)

            for detail_form in exercise_form.details:
                new_detail = ExerciseDetails(
                    repetitions=detail_form.repetitions.data,
                    weight=detail_form.weight.data,
                    exercise=new_exercise,
                )
                db.session.add(new_detail)

        db.session.commit()
        flash("Session created successfully!", "success")
        return redirect(url_for("main.homepage"))

    return render_template(
        "create_session.html", form=form, templates=Template.query.all()
    )


@workout_sessions.route("/session/<int:session_id>", methods=["GET", "POST"])
@login_required
def session(session_id):
    session = TrainingSession.query.get_or_404(session_id)
    return render_template("session.html", session=session)


@workout_sessions.route("/session/<int:session_id>/update", methods=["GET", "POST"])
@login_required
def update_session(session_id):
    session = TrainingSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
    form = SessionForm(obj=session)
    templates = [(t.id, t.name) for t in Template.query.all()]
    form.template_id.choices = [(t.id, t.name) for t in Template.query.all()]

    print(f"{form.date.data = }")
    if form.validate_on_submit():
        try:
            # deleted old session
            db.session.delete(session)

            # Create a new session
            create_session = TrainingSession(
                template_id=form.template_id.data, date=form.date.data, user_id=current_user.id
            )
            db.session.add(create_session)

            for exercise_form in form.exercises:
                new_exercise = Exercise(
                    exercise_name=exercise_form.data["exercise_name"],
                    session=create_session,
                )
                db.session.add(new_exercise)
                for detail_form in exercise_form.details:
                    new_detail = ExerciseDetails(
                        repetitions=detail_form.repetitions.data,
                        weight=detail_form.weight.data,
                        exercise=new_exercise,
                    )
                    db.session.add(new_detail)
            db.session.commit()
            flash("Session updated successfully!", "success")
            return redirect(url_for("main.homepage"))
        except Exception as e:
            db.session.rollback()
            # workout_sessions.logger.error(f"Error creating session: {e}")
            print(f"Error creating session: {e}")
            flash(
                "An error occurred while creating the session. Please try again.",
                "danger",
            )

    return render_template(
        "update_session.html", form=form, templates=templates, legend="Update Session"
    )


@workout_sessions.route("/session/<int:session_id>/delete", methods=["POST"])
@login_required
def delete_session(session_id):
    user_session = TrainingSession.query.get_or_404(session_id)
    # Make sure the template belongs to the current user
    if user_session.user_id != current_user.id:
        abort(403)
    db.session.delete(user_session)
    db.session.commit()
    flash("Your session has been deleted!", "success")
    return redirect(url_for("main.homepage"))


@workout_sessions.route("/get_last_session/<exerciseName>", methods=["GET"])
@login_required
def get_last_session(exerciseName):
    # Query for exercises that belong to the current user's training sessions
    last_session = (
        Exercise.query.join(TrainingSession)
        .filter(
            Exercise.exercise_name == exerciseName,
            TrainingSession.user_id == current_user.id
        )
        .order_by(Exercise.id.desc())
        .first()
    )
    
    if last_session:
        response = {
            "details": [
                {"repetitions": detail.repetitions, "weight": detail.weight}
                for detail in last_session.details
            ]
        }
    else:
        response = {"details": []}
    
    return jsonify(response)