from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, DateTimeField, TextAreaField, DateField
from wtforms import SubmitField
from wtforms import FileField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from wtforms.validators import Length
from Flask_Library.application import app
from wtforms.validators import Email


def validate_file_size(field):
    if field.data:
        if field.data.content_length > 10 * 1024 * 1024:
            raise ValidationError('File size should not exceed 200 MB.')


class CreateBookForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired(), Length(min=2, max=50)])
    author = StringField(label='Author', validators=[DataRequired(), Length(min=5, max=50)])
    file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(app.config['ALLOWED_EXTENSIONS'], 'Only PDFs are allowed!'),
    ])
    image_file = FileField('Image File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!')
    ])
    description = TextAreaField('Description', validators=[DataRequired()])
    date_writing = DateField('Date writing', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField(label='Create')


class DeleteBookForm(FlaskForm):
    submit = SubmitField(label='Delete')


class UpdateBookForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired(), Length(min=2, max=50)])
    author = StringField(label='Author', validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField(label='Update')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    description = TextAreaField('Description', validators=[Length(max=220)])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sign Up')


class TextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=50)])
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Save')
