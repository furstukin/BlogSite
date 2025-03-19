from datetime import date, datetime
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, desc, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List
from flask_gravatar import Gravatar
import os
# from dotenv import load_dotenv
#
# load_dotenv()

# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, PostComment

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:  # Check if the logged-in user is not the admin
            abort(403)  # Return "403 Forbidden" if the user is not authorized
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

DB_URL = os.getenv("DATABASE_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["Comments"]] = relationship(back_populates="post")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(1000))
    f_name: Mapped[str] = mapped_column(String(1000))
    l_name: Mapped[str] = mapped_column(String(1000))
    posts: Mapped[List["BlogPost"]] = relationship(back_populates="user")
    comments: Mapped[List["Comments"]] = relationship(back_populates="user")

class Comments(db.Model):
    __tablename__ = "post_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="comments")
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))
    post: Mapped["BlogPost"] = relationship(back_populates="comments")


with app.app_context():
    db.create_all()

# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Initialize the user login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.get(int(user_id))


@app.context_processor # This injects the year as a constant or global variable callable in any html code within the app. See footer copyright section for it's use.
def inject_year():
    return {'year': datetime.now().year}


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        f_name = form.f_name.data
        l_name = form.l_name.data
        email = form.email.data
        password = form.password.data
        hash_pass = generate_password_hash(password, method='scrypt', salt_length=8)
        # Check database for user
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            new_user = User(f_name=f_name, l_name=l_name, email=email, password=hash_pass)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        else:
            flash(f'A user with the email {email} already exists.')
            return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user:
            flash(f'No user with the email {email} exists.')
        else:
            hash_pass = user.password
            if check_password_hash(hash_pass, password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Invalid password')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=['POST', 'GET'])
def show_post(post_id):
    form=PostComment()
    if form.validate_on_submit():
        body = form.body.data
        if not current_user.l_name:
            author = f'{current_user.f_name}'
        else:
            author = f'{current_user.f_name} {current_user.l_name}'
        post_id = post_id
        new_comment = Comments(
            body=body,
            author=author,
            date=datetime.now().strftime("%B %d, %Y - %I:%M %p"),
            post_id=post_id,
            user_id=current_user.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))

    requested_post = db.get_or_404(BlogPost, post_id)
    comments = db.session.execute(db.select(Comments).where(Comments.post_id == post_id).order_by(desc(Comments.id))).scalars()
    return render_template("post.html", post=requested_post, form=form, comments=comments)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=f"{current_user.f_name} {current_user.l_name}",
            user_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = f"{current_user.f_name} {current_user.l_name}"
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)

    # Delete all comments associated with the post
    db.session.execute(db.delete(Comments).where(Comments.post_id == post_id))

    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5002)
