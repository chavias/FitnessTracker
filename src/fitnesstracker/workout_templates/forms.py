from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    FieldList,
    FormField,
)
from wtforms.validators import (
    DataRequired,
)
from fitnesstracker.workout_sessions.forms import ExerciseForm


class TemplateForm(FlaskForm):
    template_name = StringField("Template Name", validators=[DataRequired()])
    exercises = FieldList(
        FormField(ExerciseForm), min_entries=1
    )
    submit = SubmitField("Create Template")