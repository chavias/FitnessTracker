from fitnesstracker.models import TrainingSession, Template, TemplateExercise, Exercise, ExerciseDetails
from fitnesstracker.forms import TemplateForm, SessionForm, ExerciseForm, ExerciseDetailForm
from flask import render_template, request, redirect, jsonify, flash, url_for
from fitnesstracker import app, db
from datetime import datetime

# Routes
@app.route("/")
def homepage():
    sessions = TrainingSession.query.order_by(TrainingSession.id.desc()).all()
    return render_template("index.html", sessions=sessions)


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
    form.template_id.choices = [(t.id, t.name) for t in Template.query.all()]


    if form.validate_on_submit():
        # Create the new session (TrainingSession)
        new_session = TrainingSession(
            template_id=form.template_id.data,
            date=form.date.data
        )
        
        # Add exercises to the new session
        for exercise_form in form.exercises:
            new_exercise = Exercise(
                exercise_name=exercise_form.data['name'],
                session=new_session  # Link this exercise to the session
            )
            db.session.add(new_exercise)
            
            # Add exercise details (repetitions, weight)
            for detail_form in exercise_form.details:
                new_detail = ExerciseDetails(
                    repetitions=detail_form.repetitions.data,
                    weight=detail_form.weight.data,
                    exercise=new_exercise  # Link this detail to the exercise
                )
                db.session.add(new_detail)

        # Commit changes to the database
        db.session.commit()

        flash("Session created successfully!", "success")
        return redirect(url_for("homepage"))

    
    return render_template('new_session.html', form=form, templates=Template.query.all())



@app.route('/session/<int:session_id>', methods=['GET', 'POST'])
def session(session_id):
    session = TrainingSession.query.get_or_404(session_id)
    return render_template('session.html',session=session)


@app.route('/session/<int:session_id>/update', methods=['GET', 'POST'])
def update_session(session_id):
    session = TrainingSession.query.get_or_404(session_id)

    if request.method == 'POST':
        # Extract updated data from the form
        template_id = request.form.get('template_id')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        exercise_names = request.form.getlist('exercise[]')
        repetitions = request.form.getlist('repetitions[]')
        weights = request.form.getlist('weight[]')

        # Error handling
        errors = []
        if not date:
            errors.append("Date is required.")
        if not exercise_names:
            errors.append("At least one exercise is required.")
        if len(repetitions) != len(weights):
            errors.append("Mismatch between repetitions and weights count.")

        if errors:
            print(f"Form errors: {errors}")
            flash(" ".join(errors), "danger")
            return render_template('new_session.html', templates=Template.query.all(), session=session)

        # Process exercise details
        exercise_details = []
        exercise_names = request.form.getlist('exercise[]')

        for exercise_idx, exercise_name in enumerate(exercise_names):
            repetitions = request.form.getlist(f'repetitions_{exercise_idx}[]')
            weights = request.form.getlist(f'weight_{exercise_idx}[]')
            
            details = [
                {"repetitions": rep, "weight": wt}
                for rep, wt in zip(repetitions, weights)
            ]
            exercise_details.append({"name": exercise_name, "details": details})

        # Update the session
        session.date = date
        session.template_id = template_id


        Exercise.query.filter_by(session_id=session.id).delete()
        # db.session.delete(session)

        for ex in exercise_details:
            exercise = Exercise(
                exercise_name=ex["name"],
                session_id=session.id,  # Explicitly set session_id
                details=[
                    ExerciseDetails(
                        repetitions=det["repetitions"],
                        weight=det["weight"]
                    )
                    for det in ex["details"]
                ]
            )
            session.exercises.append(exercise)


        db.session.commit()
        flash("Session updated successfully!", "success")
        return redirect(url_for("homepage"))

    elif request.method == 'GET':
        # Prepare data for pre-filling the form
        session_data = {
            "template_id": session.template_id,
            "date": session.date.strftime('%Y-%m-%d'),
            "exercises": [
                {
                    "name": exercise.exercise_name,
                    "details": [
                        {"repetitions": det.repetitions, "weight": det.weight}
                        for det in exercise.details
                    ]
                }
                for exercise in session.exercises
            ]
        }
        for exercise in session.exercises:
            print(f"{exercise.exercise_name =}")
        return render_template('update_session.html', templates=Template.query.all(), session=session_data)




@app.route("/session/<int:session_id>/delete", methods=['POST'])
def delete_session(session_id):
    user_session = TrainingSession.query.get_or_404(session_id)  # Use a different name for the variable
    db.session.delete(user_session)
    db.session.commit()
    flash('Your session has been deleted!', 'success')
    return redirect(url_for('homepage'))





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



