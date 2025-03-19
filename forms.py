from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField
from wtforms.fields.simple import StringField, PasswordField, SubmitField, EmailField, TelField
from wtforms.validators import DataRequired, Length


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterForm(FlaskForm):
    f_name = StringField('First Name*', validators=[DataRequired()])
    l_name = StringField(' Last Name')
    email = EmailField("Email*", validators=[DataRequired()])
    password = PasswordField("Password*", validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    submit = SubmitField("Submit Registration")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class PostComment(FlaskForm):
    body = CKEditorField("Comment on post", validators=[DataRequired()])
    submit = SubmitField("Post Comment")

class ContactMe(FlaskForm):
    name = StringField('Name*', validators=[DataRequired()])
    email = EmailField("Email*", validators=[DataRequired()])
    phone = TelField('Telephone')
    body = CKEditorField("Message*", validators=[DataRequired()])
    submit = SubmitField("Send Email")