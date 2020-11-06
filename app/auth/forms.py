from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User

def password_check(form, field):
    '''
    Custom validator that checks to see if two passwords are equal.
    
    :param form:        The form as an object.
    :param field:       The field, as an object.
    :onerror:           If the two passwords are not equal, a validation error is raised.
    '''
    if form.password.data != form.verify_password.data:
        raise ValidationError('Passwords must match.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    first_name = StringField("What's your first name?", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("What's your surname?", validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password (8 characters minimum)', validators=[DataRequired(), Length(min=8)])
    verify_password = PasswordField('Verify password', validators=[DataRequired(), password_check])
    email_opt_in = BooleanField("Want to receive email updates about new products we're developing? (No spam, we promise.)")
    submit = SubmitField('Register')

    def validate_email(self, email):
        '''
        If an account already exists with that email address, this check raises a ValidationError.
        '''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired()])
    verify_password = PasswordField('Verify password', validators=[DataRequired(), password_check])
    submit = SubmitField('Submit')