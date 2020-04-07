from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms.fields.html5 import DateField
from app.models import User

# User Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired(message = "Username is required.")], render_kw = {"placeholder": "Username"})
    password = PasswordField("Password", validators = [DataRequired(message = "Password is required.")], render_kw = {"placeholder": "Password"})
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")

# User Registration Form
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired(message = "Username is required.")], render_kw = {"placeholder": "Username"})
    firstname = StringField("First Name", validators = [DataRequired(message = "First Name is required.")], render_kw = {"placeholder": "First Name"})
    middlename = StringField("Middle Name", render_kw = {"placeholder": "Middle Name"})
    lastname = StringField("Last Name", validators = [DataRequired(message = "Last Name is required.")], render_kw = {"placeholder": "First Name"})
    dob = DateField("Date Of Birth", validators = [DataRequired(message = "Date Of Birth is required.")], format = "%Y-%m-%d")
    email = StringField("Email", validators = [DataRequired(message = "Email Address is required.")], render_kw = {"placeholder": "Email Address"})
    password = PasswordField("Password", validators = [DataRequired(message = "Password is required.")], render_kw = {"placeholder": "Password"})
    confirm_password = PasswordField("Repeat Password", validators = [DataRequired(message = "Password Confirmation is required."), EqualTo("password")], render_kw = {"placeholder": "Confirm Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError("Username Already Exists! Please Use A Different Username.")

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError("Email Address Already Exists! Please Use A Different Email Address.")

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(message = "Post Title is required.")], render_kw = {"placeholder": "Post Title"})
    body = TextAreaField("Body", validators=[DataRequired(message = "Content is required.")], render_kw = {"placeholder": "Content"})
    image = FileField("Upload Image", validators=[FileAllowed(["jpg", "png"])])
    video = FileField("Upload Video", validators=[FileAllowed(["mp4", "mov"])])
    submit = SubmitField("Post")


