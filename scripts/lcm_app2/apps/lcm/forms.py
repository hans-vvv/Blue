from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, \
    SelectField, PasswordField, TimeField
from wtforms.validators import InputRequired, DataRequired, Length, EqualTo


class AddSiteForm(FlaskForm):
    sitename = StringField('SiteNaam')

class DeleteSiteForm(FlaskForm):
    sitename = SelectField('SiteNaam', choices = [])


class SelectSiteForm(FlaskForm):
    sitename = SelectField(
        'SiteNaam',
        validators=[InputRequired()],
        choices = [],
    )

