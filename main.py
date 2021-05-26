from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# ## retrieve all blog posts
# posts = db.session.query(BlogPost).all()


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/make-post", methods=['GET', 'POST'])
def create_post():
    if request.method == 'GET':
        post_field = CreatePostForm()
        return render_template("make-post.html", form=post_field)

    elif request.method == 'POST':

        new_post = BlogPost(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            # generates date automatically
            date=date.today().strftime("%B %d, %Y"),
            body=request.form.get('body'),
            author=request.form.get('author'),
            img_url=request.form.get('img_url'),
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('get_all_posts'))


@app.route("/edit-post/<int:index>", methods=['GET', 'POST'])
def edit_post(index):
    post_to_edit = BlogPost.query.get(index)

    if request.method == 'GET':
        # editing variable changes h1 in make-post.html
        editing = True
        # form is prefilled with post's information
        filled_form = CreatePostForm(
            title=post_to_edit.title,
            subtitle=post_to_edit.subtitle,
            body=post_to_edit.body,
            author=post_to_edit.author,
            img_url=post_to_edit.img_url,
        )
        return render_template("make-post.html", form=filled_form, edit=editing)

    elif request.method == 'POST':
        post_to_edit.title = request.form.get('title')
        post_to_edit.subtitle = request.form.get('subtitle')
        post_to_edit.body = request.form.get('body')
        post_to_edit.author = request.form.get('author')
        post_to_edit.img_url = request.form.get('img_url')

        db.session.commit()

        return redirect(url_for('get_all_posts'))

@app.route('/delete/<int:index>')
def delete_post(index):
    post_to_delete = BlogPost.query.get(index)

    if post_to_delete:
        db.session.delete(post_to_delete)
        db.session.commit()

    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
