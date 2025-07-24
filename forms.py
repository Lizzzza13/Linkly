from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, Length, equal_to, Email, Optional


class URLForm(FlaskForm):
    original_url = StringField("Enter URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Shorten")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=25)])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired(), equal_to("password")])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class UserForm(FlaskForm):
    img = FileField("Profile Image", validators={FileAllowed(["png", "jpeg", "jpg"])})
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("New Password", validators=[Optional(), Length(min=8, max=25)])
    repeat_password = PasswordField("Repeat password", validators=[Optional(), equal_to("password")])
    submit = SubmitField("Update Profile")


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Profile Image', validators=[FileAllowed(["png", "jpeg", "jpg"])])
    submit = SubmitField('Save Changes')
