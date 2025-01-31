from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from fitnesstracker import db
from fitnesstracker.models import Exercise, ExerciseDetails, Template, TemplateExercise, TrainingSession
from fitnesstracker.workout_templates.forms import TemplateForm


workout_templates = Blueprint('workout_templates',
                              __name__,
                              static_folder='static',
                              static_url_path='/workout_templates/static', 
                              template_folder='../templates')


@workout_templates.route("/create_template", methods=["GET", "POST"])
def create_template():
    form = TemplateForm()

    if form.validate_on_submit():
        if form.submit.data:  # Create Template logic
            # Fetch form data
            template_name = form.template_name.data
            exercises = [exercise.exercise_name.data for exercise in form.exercises]

            # Create a new Template object
            new_template = Template(name=template_name)

            # Add exercises to the template
            new_template.exercises = [
                TemplateExercise(exercise=exercise) for exercise in exercises
            ]

            # Save the template and associated exercises
            db.session.add(new_template)
            db.session.commit()

            flash("Template added successfully!", "success")

            # Debugging: Print saved template and exercises
            print(f"New Template Added: {new_template.id} - {new_template.name}")
            for exercise in new_template.exercises:
                print(f"Exercise: {exercise.exercise}")

            # Redirect to the same page to avoid duplicate form submissions
            return redirect("/create_template")

    # Fetch all templates with their associated exercises
    templates = Template.query.all()

    # Create a dictionary for rendering template data
    template_data = {t.id: [e.exercise for e in t.exercises] for t in templates}

    return render_template(
        "create_template.html", form=form, templates=templates, template_data=template_data
    )


@workout_templates.route("/template/<int:template_id>")
def template(template_id):
    template = Template.query.get_or_404(template_id)
    return render_template("template.html", template=template)


@workout_templates.route("/template/<int:template_id>/update", methods=["GET", "POST"])
def update_template(template_id):
    template = Template.query.get_or_404(template_id)
    form = TemplateForm()

    if form.validate_on_submit():
        template.exercises = [] 
        # Create new Exercise instances based on form data
        for exercise_form in form.exercises:
            exercise = TemplateExercise(exercise=exercise_form.exercise_name.data)
            template.exercises.append(exercise)

        db.session.commit()
        flash("Your template has been updated!", "success")
        return redirect(url_for("workout_templates.template", template_id=template.id))

    elif request.method == "GET":
        # Pre-fill the form with existing exercise data
        form.template_name.data = template.name
        if template.exercises:
            form.exercises[0].exercise_name.data = template.exercises[
                0
            ].exercise
        for exercise in template.exercises[1:]:
            form.exercises.append_entry({"exercise_name": exercise.exercise})

    return render_template("create_template.html", form=form, legend="Update template")


@workout_templates.route("/template/<int:template_id>/delete", methods=["POST"])
def delete_template(template_id):
    template = Template.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash("Your template has been deleted!", "success")
    return redirect(url_for("main.homepage"))


@workout_templates.route("/get_template/<int:template_id>", methods=["GET"])
def get_template(template_id):
    # Fetch the template with the provided ID
    template = Template.query.get_or_404(template_id)
    exercises = []

    for template_exercise in template.exercises:
        # Find the latest exercise session that used this exercise
        last_exercise = (
            db.session.query(Exercise)
            .join(TrainingSession)
            .filter(
                Exercise.exercise_name == template_exercise.exercise,
                TrainingSession.template_id
                == template.id,  # Ensure it's from the right template
            )
            .order_by(TrainingSession.date.desc())
            .first()
        )

        # Get the most recent ExerciseDetails from the latest exercise session
        if last_exercise:
            last_exercise_detail = (
                db.session.query(ExerciseDetails)
                .filter(ExerciseDetails.exercise_id == last_exercise.id)
                .order_by(ExerciseDetails.id.desc())
                .first()
            )

            if last_exercise_detail:
                # Use the most recent exercise details if found
                default_sets = last_exercise_detail.repetitions
                default_reps = last_exercise_detail.repetitions
                default_weight = last_exercise_detail.weight
            else:
                # Set fallback default values if no ExerciseDetails are found
                default_sets = 3
                default_reps = 10
                default_weight = 20
        else:
            # Fallback if no Exercise session was found
            default_sets = 3
            default_reps = 10
            default_weight = 20

        exercises.append(
            {
                "exercise": template_exercise.exercise,
                "default_sets": default_sets,
                "default_reps": default_reps,
                "default_weight": default_weight,
            }
        )

    return jsonify({"exercises": exercises})