from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField


class VerifyForm(FlaskForm):
    verify = BooleanField("Verified")
    submit = SubmitField('Submit')
