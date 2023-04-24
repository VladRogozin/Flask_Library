import os
import uuid
from datetime import datetime
from flask import send_file

from Flask_Library.application.models import Book, BookRating, Text
from Flask_Library.application.forms import CreateBookForm, TextForm
from Flask_Library.application.forms import DeleteBookForm
from Flask_Library.application.forms import UpdateBookForm
from Flask_Library.application import app
from Flask_Library.application import models
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from Flask_Library.application.models import User
from Flask_Library.application.forms import LoginForm, RegistrationForm
from Flask_Library.application import db


@app.route('/')
def index():
    return render_template('index.html', title="Home", content='HELLO', hello='gg')


@app.route('/book/list')
def read_books():
    books = Book.query.all()
    book = Book

    return render_template('list.html', book=book, title='List of books', books=books)


@app.route('/book/rate', methods=['POST'])
def rate_book():
    book_id = request.form['book_id']
    rating = request.form['rating']
    user_id = current_user.id
    existing_rating = BookRating.query.filter_by(book_id=book_id, user_id=user_id).first()
    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = BookRating(rating=rating, book_id=book_id, user_id=user_id)
        db.session.add(new_rating)
    db.session.commit()
    return redirect(url_for('read_books'))


@app.route('/book/my')
@login_required
def my_books():
    user_id = current_user.id
    books = Book.query.filter_by(user_id=user_id).all()
    return render_template('my_books.html', books=books)


@app.route('/book/detail/<int:pk>')     # /book/detail/4
def detail(pk):
    book = Book.query.filter_by(id=pk).first()

    if book is None:
        return render_template('index.html', title='Page not found', content='404 - Page not found')

    return render_template('detail.html', title='Book detail', book=book)


@app.route('/book/download/<int:pk>')
@login_required
def download(pk):
    book = Book.query.filter_by(id=pk).first()

    filename = book.pdf_filename
    filepath = os.path.join(app.config['BOOK_UPLOAD_FOLDER'], filename)

    return send_file(filepath, as_attachment=True)


@app.route('/book/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateBookForm()

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        file = form.file.data
        image_file = form.image_file.data
        description = form.description.data
        date_writing = form.date_writing.data

        extension = file.filename.split('.')[-1]
        filename = str(uuid.uuid4()) + '.' + extension
        file.save(os.path.join(app.config['BOOK_UPLOAD_FOLDER'], filename))

        image_extension = image_file.filename.split('.')[-1]
        image_filename = str(uuid.uuid4()) + '.' + image_extension
        image_file.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], image_filename))

        book = Book(title=title,
                    author=author,
                    description=description,
                    date_writing=date_writing,
                    created=datetime.utcnow()
                    )

        book.pdf_filename = filename
        book.image_filename = image_filename
        book.user = current_user

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('read_books'))

    return render_template('create.html', title='Create new book', form=form)


@app.route('/book/my_write')
@login_required
def my_write_books():
    user_id = current_user.id
    books = Text.query.filter_by(user_id=user_id).all()
    return render_template('my_write_books.html', books=books)


def save_text(user_id, title, content):
    text = Text(user_id=user_id, title=title, content=content)
    db.session.add(text)
    db.session.commit()


def load_text(text_id):
    text = Text.query.filter_by(id=text_id).first()
    return text


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    form = TextForm()
    user_id = current_user.id
    if form.validate_on_submit():
        text = Text(content=form.text.data, title=form.title.data, user_id=user_id)
        db.session.add(text)
        db.session.commit()
        flash('Text saved!')
    return render_template('editor.html', form=form)


@app.route('/edit_text/<int:text_id>')
def edit_text(text_id):
    text = Text.query.filter_by(id=text_id).first()
    return render_template('edit_text.html', text=text)


@app.route('/book/update/<int:pk>', methods=['GET', 'POST'])
@login_required
def update(pk):
    book = Book.query.get(pk)
    form = UpdateBookForm()

    if book.user_id != current_user.id:
        flash('You are not authorized to delete this book.')
        return redirect(url_for('detail', pk=book.id))
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        db.session.commit()
        return redirect(url_for('read_books'))
    elif request.method == 'GET':
        form.title.data = book.title
        form.author.data = book.author

    return render_template('update.html', title='Update book', book=book, form=form)


@app.route('/book/delete/<int:pk>', methods=['GET', 'POST'])
@login_required
def delete(pk):
    book = Book.query.get(pk)
    form = DeleteBookForm()

    if book.user_id != current_user.id:
        flash('You are not authorized to delete this book.')
        return redirect(url_for('detail', pk=book.id))

    if form.validate_on_submit():
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('read_books'))

    return render_template('delete.html', title='Delete book', book=book, form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        books = Book.query.filter(
            (Book.author.contains(search_term)) | (Book.title.contains(search_term))
        ).all()
        return render_template('results.html', search_term=search_term, books=books)
    else:
        return render_template('index.html')


@app.route('/profile/<int:pk>')
def profile(pk):
    user = User.query.filter_by(id=pk).first()
    return render_template('my_profile.html', user=user)


@app.route('/book/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            print('User found in database')
            if check_password_hash(user.password, form.password.data):
                print('Password is correct')
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('read_books'))
            else:
                flash('Invalid username or password', 'danger')
        else:
            flash('User not found', 'danger')

    return render_template('login.html', form=form)


@app.route('/book/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/book/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pwd = generate_password_hash(form.password.data)
        photo = form.photo.data

        image_extension = photo.filename.split('.')[-1]
        image_filename = str(uuid.uuid4()) + '.' + image_extension
        photo.save(os.path.join(app.config['IMAGE_PROFILE_FOLDER'], image_filename))

        user = User(username=form.username.data, password=hash_pwd, first_name=form.first_name.data,
                    last_name=form.last_name.data, email=form.email.data, description=form.description.data)
        user.photo_filename = image_filename

        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.context_processor
def inject_current_user():
    return dict(current_user=current_user)


app.run(debug=True, port=12345)

