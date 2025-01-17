from fitnesstracker.models import TrainingSession, Template, TemplateExercise, Exercise
from flask import render_template, request, redirect, jsonify, flash
from fitnesstracker import app, db
from datetime import datetime

# Routes
@app.route("/")
def homepage():
    sessions = TrainingSession.query.order_by(TrainingSession.id.desc()).limit(10).all()
    session_data = []

    for session in sessions:
        exercises = [
            {"exercise": ex.exercise, "sets": ex.sets, "reps": ex.reps, "weight": ex.weight}
            for ex in session.exercises
        ]
        session_data.append({
            "session_id": session.id,
            "date": session.date.strftime('%Y-%m-%d'),
            "template_name": session.template.name if session.template else None,
            "exercises": exercises,
        })

    return render_template("index.html", session_data=session_data)

@app.route("/templates", methods=["GET", "POST"])
def templates():
    if request.method == "POST":
        # Fetch form data
        template_name = request.form["template_name"]
        exercises = request.form.getlist("exercise[]")

        # Create a new Template object
        new_template = Template(name=template_name)

        # Add exercises to the template
        new_template.exercises = [TemplateExercise(exercise=exercise) for exercise in exercises]

        # Save the template and associated exercises
        db.session.add(new_template)
        db.session.commit()

        flash('added template', 'success')
        # Debugging: Check the saved template
        print(f"New Template Added: {new_template.id} - {new_template.name}")
        for exercise in new_template.exercises:
            print(f"Exercise: {exercise.exercise}")

        return redirect("/templates")

    # Query all templates with their exercises
    templates = Template.query.all()
    print(f"Templates: {templates}")

    # Create a dictionary to pass data to the template
    template_data = {t.id: [e.exercise for e in t.exercises] for t in templates}
    print(f"Template Data: {template_data}")

    return render_template("templates.html", templates=templates, template_data=template_data)



@app.route("/get_last_session/<exercise>", methods=["GET"])
def get_last_session(exercise):
    last_exercise = Exercise.query.filter_by(exercise=exercise).order_by(Exercise.session_id.desc()).first()

    if last_exercise:
        return jsonify({"sets": last_exercise.sets, "reps": last_exercise.reps, "weight": last_exercise.weight})
    else:
        return jsonify({"sets": "", "reps": "", "weight": ""})  # No prior session


@app.route("/add", methods=["GET", "POST"])
def add_session():
    if request.method == "POST":
        date = request.form["date"]
        template_id = request.form["template_id"]
        exercises = request.form.getlist("exercise[]")
        sets = request.form.getlist("sets[]")
        reps = request.form.getlist("reps[]")
        weights = request.form.getlist("weight[]")

        new_session = TrainingSession(date=datetime.strptime(date, "%Y-%m-%d"), template_id=template_id)
        db.session.add(new_session)
        db.session.commit()

        for exercise, set_count, rep_count, weight in zip(exercises, sets, reps, weights):
            new_exercise = Exercise(
                session_id=new_session.id,
                exercise=exercise,
                sets=int(set_count),
                reps=int(rep_count),
                weight=float(weight)
            )
            db.session.add(new_exercise)

        db.session.commit()
        flash('added session', 'success')
        return redirect("/")

    templates = Template.query.all()
    template_exercises = {t.id: [e.exercise for e in t.exercises] for t in templates}

    return render_template("add.html", templates=templates, template_exercises=template_exercises)


@app.route("/get_template/<int:template_id>")
def get_template(template_id):
    template = Template.query.get_or_404(template_id)
    exercises = [{"exercise": ex.exercise} for ex in template.exercises]
    return jsonify({"exercises": exercises})