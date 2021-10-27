from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    name = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterUser(FlaskForm):
    name = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    comfirm = PasswordField('Comfim Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Register')

class FailureReport(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RepairReport(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[DataRequired()])
    completed = RadioField('Completed')
    submit = SubmitField('Submit')

class PMReport(FlaskForm):
    submit = SubmitField('Complete')