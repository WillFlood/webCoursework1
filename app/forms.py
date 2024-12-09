from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from datetime import date
from .models import Register

def checkDate(form, field): #Doing this as it means a user cannot create an event that is in the past
    if field.data < date.today():
        raise ValidationError("Date cannot be in the past.")


class EventForm(FlaskForm):
    eventTitle = StringField('Event Title', validators=[DataRequired(), Length(max=100)]) #Ensures the user doesn't break the system by adding too many characters
    eventDate = DateField('Event Date', format='%Y-%m-%d', validators=[DataRequired(), checkDate])
    eventPlace = StringField('Event Location', validators=[DataRequired(), Length(max=250)])
    eventCategory = SelectField('Category', choices=[ 
        ('Music', 'Music'),
        ('Art', 'Art'),
        ('Charity', 'Charity'),
        ('Voluntary', 'Voluntary'),
        ('Education', 'Education'),
        ('Technology', 'Technology'),
        ('Sports', 'Sports'),
        ('Careers and business', 'Careers and business'),
        ('Travel and Outdoor', 'Travel and Outdoor'),
        ('Leisure', 'Leisure'),
        ('Other', 'Other') #Form including all the categories
    ], validators=[DataRequired()])
    eventDescription = TextAreaField('Description')
    submit = SubmitField('Create Event')


def checkEmail(form, field): #Checking whether a user registering has already got an email registered
    existing_user = Register.query.filter_by(email=field.data).first()
    if existing_user:
        raise ValidationError('Email is already registered.')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email(), checkEmail])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirmPassword = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')

class EditPasswordForm(FlaskForm):
    oldPassword = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
    newPassword = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirmPassword = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('newPassword', message='Passwords must match')])
    submit = SubmitField('Update Password')

class EditEventForm(FlaskForm):
    eventTitle = StringField('Title', validators=[DataRequired(), Length(max=100)])
    eventDate = DateField('Date', validators=[DataRequired()])
    eventPlace = StringField('Place', validators=[DataRequired(), Length(max=200)])
    eventCategory = SelectField(
        'Category', 
        choices=[('Music', 'Music'), ('Sports', 'Sports'), ('Education', 'Education'), ('Other', 'Other')],
        validators=[DataRequired()]
    )
    eventDescription = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Update Event')



