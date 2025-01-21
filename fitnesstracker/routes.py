from fitnesstracker.models import TrainingSession, Template, TemplateExercise, Exercise, ExerciseDetails
from fitnesstracker.forms import TemplateForm, SessionForm, ExerciseForm, ExerciseDetailForm
from flask import render_template, request, redirect, jsonify, flash, url_for
from fitnesstracker import app, db
from datetime import datetime

# Routes
@app.route("/")
def homepage():
    sessions = TrainingSession.query.order_by(TrainingSession.id.desc()).limit(10).all()
    session_data = []

    for session in sessions:
        exercises = []
        for ex in session.exercises:
            # Fetch the corresponding details for each exercise (sets, reps, weight)
            details = [
                {"sets": detail.repetitions, "reps": detail.repetitions, "weight": detail.weight}
                for detail in ex.details
            ]
            exercises.append({
                "exercise_name": ex.exercise_name,  # Correct field name
                "details": details
            })

        session_data.append({
            "session_id": session.id,
            "date": session.date.strftime('%Y-%m-%d'),
            "template_name": session.template.name if session.template else None,
            "exercises": exercises,
        })

    return render_template("index.html", session_data=session_data)




@app.route('/templates', methods=['GET', 'POST'])
def templates():
    form = TemplateForm()

    if form.validate_on_submit():
        if form.submit.data:  # Create Template logic
            # Fetch form data
            template_name = form.template_name.data
            exercises = [exercise.exercise_name.data for exercise in form.exercises]

            # Create a new Template object
            new_template = Template(name=template_name)

            # Add exercises to the template
            new_template.exercises = [TemplateExercise(exercise=exercise) for exercise in exercises]

            # Save the template and associated exercises
            db.session.add(new_template)
            db.session.commit()

            flash('Template added successfully!', 'success')

            # Debugging: Print saved template and exercises
            print(f"New Template Added: {new_template.id} - {new_template.name}")
            for exercise in new_template.exercises:
                print(f"Exercise: {exercise.exercise}")

            # Redirect to the same page to avoid duplicate form submissions
            return redirect('/templates')

    # Fetch all templates with their associated exercises
    templates = Template.query.all()

    # Create a dictionary for rendering template data
    template_data = {t.id: [e.exercise for e in t.exercises] for t in templates}

    return render_template('templates.html', form=form, templates=templates, template_data=template_data)


@app.route("/template/<int:template_id>")
def template(template_id):
    template = Template.query.get_or_404(template_id)
    return render_template('template.html', template=template)


@app.route("/template/<int:template_id>/update", methods=['GET', 'POST'])
def update_template(template_id):
    template = Template.query.get_or_404(template_id)
    form = TemplateForm()

    if form.validate_on_submit():
        # Clear existing exercises (if needed) and add new ones
        template.exercises = []  # Empty the existing exercises

        # Create new Exercise instances based on form data
        for exercise_form in form.exercises:
            exercise = TemplateExercise(exercise=exercise_form.exercise_name.data)
            template.exercises.append(exercise)  # Add the exercise to the template

        db.session.commit()
        flash('Your template has been updated!', 'success')
        return redirect(url_for('template', template_id=template.id))

    elif request.method == 'GET':
        # Pre-fill the form with existing exercise data
        form.template_name.data = template.name
        if template.exercises:
            form.exercises[0].exercise_name.data = template.exercises[0].exercise  # Set the first exercise
        # form.exercises = template.exercises
        for exercise in template.exercises[1:]:
            form.exercises.append_entry({'exercise_name': exercise.exercise})

    return render_template('templates.html', form=form, legend='Update template')


@app.route("/template/<int:template_id>/delete", methods=['POST'])
def delete_template(template_id):
    template = Template.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash('Your template has been deleted!', 'success')
    return redirect(url_for('homepage'))



@app.route('/new_session', methods=['GET', 'POST'])
def new_session():
    form = SessionForm()

    # Populate the template dropdown with templates
    form.template_id.choices = [(template.id, template.name) for template in Template.query.all()]

    if request.method == 'POST':
        # Debug POST data
        print(f"POST data: {request.form}")
        print(f"Flask form: {form.data}")
        

        # Check if the form validates
        if form.validate_on_submit():
            print("Form validation successful")
            
            # Process exercises and save the session
            exercises = []
            for exercise_form in form.exercises.entries:
                exercise_name = exercise_form.name.data
                exercise_details = [
                    {
                        "repetitions": detail.repetitions.data,
                        "weight": detail.weight.data
                    }
                    for detail in exercise_form.details.entries
                ]
                exercises.append({"name": exercise_name, "details": exercise_details})

            print(f"Exercises to save: {exercises}")

            # Create a new TrainingSession object and save it
            new_session = TrainingSession(
                date=form.date.data,
                template_id=form.template_id.data,
                exercises=[
                    Exercise(
                        exercise_name=ex["name"],
                        details=[
                            ExerciseDetails(repetitions=det["repetitions"], weight=det["weight"])
                            for det in ex["details"]
                        ]
                    )
                    for ex in exercises
                ]
            )
            db.session.add(new_session)
            db.session.commit()

            flash("Session created successfully!", "success")
            return redirect(url_for("new_session"))
        else:
            # If validation fails, debug form errors
            print(f"Form errors: {form.errors}")
            print(f"Exercises submitted: {form.exercises.entries}")

    elif request.method == 'GET' and form.template_id.data:
        # Load exercises if a template is selected (for initial GET request)
        selected_template = Template.query.get(form.template_id.data)
        form.exercises.entries.clear()
        for template_exercise in selected_template.exercises:
            exercise_form = ExerciseForm(name=template_exercise.exercise)
            for detail in template_exercise.details:
                exercise_form.details.append_entry(
                    {"repetitions": detail.repetitions, "weight": detail.weight}
                )
            form.exercises.append_entry(exercise_form)

    return render_template('new_session.html', form=form, templates=Template.query.all())




@app.route('/get_template/<int:template_id>', methods=['GET'])
def get_template(template_id):
    # Fetch the template with the provided ID
    template = Template.query.get_or_404(template_id)
    exercises = []

    for template_exercise in template.exercises:
        # Find the latest exercise session that used this exercise
        last_exercise = db.session.query(Exercise).join(TrainingSession).filter(
            Exercise.exercise_name == template_exercise.exercise,
            TrainingSession.template_id == template.id  # Ensure it's from the right template
        ).order_by(TrainingSession.date.desc()).first()

        # Get the most recent ExerciseDetails from the latest exercise session
        if last_exercise:
            last_exercise_detail = db.session.query(ExerciseDetails).filter(
                ExerciseDetails.exercise_id == last_exercise.id
            ).order_by(ExerciseDetails.id.desc()).first()

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

        exercises.append({
            'exercise': template_exercise.exercise,
            'default_sets': default_sets,
            'default_reps': default_reps,
            'default_weight': default_weight
        })

    return jsonify({'exercises': exercises})


@app.route('/get_last_session/<exerciseName>', methods=['GET'])
def get_last_session(exerciseName):
    # Query the database for the last session of this exercise
    last_session = Exercise.query.filter_by(exercise_name=exerciseName).order_by(Exercise.id.desc()).first()
    if last_session:
        # Extract details to send back as JSON
        response = {
            "details": [
                {
                    "repetitions": detail.repetitions,
                    "weight": detail.weight
                }
                for detail in last_session.details
            ]
        }
    else:
        # No previous session found for the exercise
        response = {"details": []}
    return jsonify(response)
