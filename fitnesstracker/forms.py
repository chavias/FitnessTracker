from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FieldList, FormField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class RegistrationFrom(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class RegistrationFrom(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Subform for exercises
class ExerciseTemplateForm(FlaskForm):
    exercise_name = StringField('Exercise Name', validators=[DataRequired()])

# Form for Templates
class TemplateForm(FlaskForm):
    template_name = StringField('Template Name', validators=[DataRequired()])
    exercises = FieldList(FormField(ExerciseTemplateForm), min_entries=1)  # Dynamically add exercise rows
    add_exercise = SubmitField('Add Exercise')
    submit = SubmitField('Create Template')

''' Session Form '''
class ExerciseDetailForm(FlaskForm):
    repetitions = IntegerField('Repetitions', validators=[DataRequired(), NumberRange(min=1)])
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    delete = SubmitField('Remove')

class ExerciseForm(FlaskForm):
    name = StringField('Exercise Name', validators=[DataRequired()])
    details = FieldList(FormField(ExerciseDetailForm), min_entries=1)
    add_detail = SubmitField('Add Detail')
    delete = SubmitField('Remove Exercise')

class SessionForm(FlaskForm):
    template_id = SelectField(
        'Template',
        choices=[],  # Populated dynamically in the route
        coerce=int,
        validators=[DataRequired()]
    )
    exercises = FieldList(FormField(ExerciseForm), min_entries=0)  # Use FormField for ExerciseForm
    add_exercise = SubmitField('Add Exercise')
    submit = SubmitField('Save Session')

