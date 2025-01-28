from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    FieldList,
    FormField,
    IntegerField,
    FloatField,
    SelectField,
    DateField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    NumberRange,
    InputRequired,
)

""" Registration and Login Forms """
class RegistrationFrom(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


""" Template Forms """
# class ExerciseTemplateForm(FlaskForm):
#     exercise_name = StringField("Exercise Name", validators=[DataRequired()])

class ExerciseDetailForm(FlaskForm):
    repetitions = IntegerField("Repetitions", validators=[InputRequired()])
    weight = FloatField("Weight", validators=[InputRequired()])

class ExerciseForm(FlaskForm):
    exercise_name = StringField("Exercise Name", validators=[DataRequired()])
    details = FieldList(FormField(ExerciseDetailForm), min_entries=0)

class TemplateForm(FlaskForm):
    template_name = StringField("Template Name", validators=[DataRequired()])
    exercises = FieldList(
        FormField(ExerciseForm), min_entries=1
    )
    # add_exercise = SubmitField('Add Exercise')
    submit = SubmitField("Create Template")

class SessionForm(FlaskForm):
    template_id = SelectField("Template", coerce=int)
    date = DateField("Date", validators=[DataRequired()])
    exercises = FieldList(FormField(ExerciseForm), min_entries=1)
    submit = SubmitField("Submit")
