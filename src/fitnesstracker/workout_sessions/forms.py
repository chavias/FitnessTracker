from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    FieldList,
    FormField,
    IntegerField,
    FloatField,
    SelectField,
    DateField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
)


class ExerciseDetailForm(FlaskForm):
    repetitions = IntegerField("Repetitions", validators=[InputRequired()])
    weight = FloatField("Weight", validators=[InputRequired()])


class ExerciseForm(FlaskForm):
    exercise_name = StringField("Exercise Name", validators=[DataRequired()])
    details = FieldList(FormField(ExerciseDetailForm), min_entries=0)


class SessionForm(FlaskForm):
    template_id = SelectField("Template", coerce=int)
    date = DateField("Date", validators=[DataRequired()])
    exercises = FieldList(FormField(ExerciseForm), min_entries=1)
    submit = SubmitField("Submit")
