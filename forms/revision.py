from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class RevisionForm(FlaskForm):
    content = TextAreaField("Содержание", validators=[DataRequired()])
    description = StringField("Описание правки", validators=[DataRequired()])
    submit = SubmitField('Подтвердить отправку')
