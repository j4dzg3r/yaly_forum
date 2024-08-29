from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class RevisionForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()], render_kw={"class": "text-area-field"})
    description = StringField("Revision description", validators=[DataRequired()])
    submit = SubmitField("Publish changes")
