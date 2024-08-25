from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class RevisionForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    description = StringField("Revision description", validators=[DataRequired()])
    submit = SubmitField('Submit')
