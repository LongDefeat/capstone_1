from ast import Str
from operator import length_hint
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    

class LoginForm(FlaskForm):
    """Form for user to login."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    
class EditProfileForm(FlaskForm):
    """Edit a user's profile."""

    username = StringField('Username')
    password = PasswordField('Password')
    email = StringField('E-mail')
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    bio = TextAreaField('Bio', description="Tell us about you...")

class SearchDrink(FlaskForm):
    """Form to search for a drink."""

    search = StringField('Search')
