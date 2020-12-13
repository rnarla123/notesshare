from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
import pyotp
import re


from .models import User


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class NotesReviewForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    rating = IntegerField(
        "Rating", validators=[InputRequired(), NumberRange(min=1, max=5)]
    )
    submit = SubmitField("Enter Comment")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")

    def validate_password(self, password):
        password = password.data
        if (len(password)<8): 
            raise ValidationError("Must be 8 or more characters")
        elif not re.search("[a-z]", password): 
            raise ValidationError("Lowercase needed")
        elif not re.search("[A-Z]", password): 
            raise ValidationError("Uppercase needed")
        elif not re.search("[0-9]", password): 
            raise ValidationError("Numbers needed")
        elif not re.search("[_@$]", password): 
            raise ValidationError("_ or @ or $ needed")
        elif re.search("\s", password): 
            raise ValidationError("Try again")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    token = StringField('Token', validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField("Login")

    def validate_token(self, token):
        user = User.objects(username=self.username.data).first()
        if user is not None:
            tok_verified = pyotp.TOTP(user.otp_secret).verify(token.data)
            if not tok_verified:
                raise ValidationError("Invalid Token")

class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "New Username:", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")


class UploadNotesForm(FlaskForm):
    title=StringField("Title", validators=[InputRequired()])
    class_name=StringField("Class Name", validators=[InputRequired()])
    file = FileField('File', validators=[
        FileRequired(), 
        FileAllowed(['pdf'], 'PDFs Only!')
    ])
    submit_pic = SubmitField('Submit File')