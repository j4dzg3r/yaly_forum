from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    job = StringField('Заголовок', validators=[DataRequired()])
    work_size = IntegerField("Длительность в часах", validators=[DataRequired()])
    collaborators = StringField("Исполнители (через запятую и пробел)", validators=[DataRequired()])
    start_date = DateField("Начало работы")
    end_date = DateField("Конец работы")
    is_finished = BooleanField("Завершено")
    submit = SubmitField('Применить')
