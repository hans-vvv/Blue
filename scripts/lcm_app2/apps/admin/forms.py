from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, \
    SelectField, PasswordField, TimeField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired()])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=4, max=40, message='min 4, max 40 chars')])
    confirm = PasswordField(
        'Confirm password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')])


class AddUserForm(FlaskForm):
    username = StringField('Gebruikersnaam')
    userrole = SelectField('Gebruikersrol', choices = [])

class AddUserAuthForm(FlaskForm):
    username = SelectField('Gebruikersnaam', choices = [])
    userrole = SelectField('Gebruikersrol', choices = [])

