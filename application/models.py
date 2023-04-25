from flask_login import UserMixin

from application import db, manager
from datetime import datetime


class Book(db.Model):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    date_writing = created = db.Column(db.DateTime)
    description = db.Column(db.String(220), nullable=True)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pdf_filename = db.Column(db.String(100), nullable=True)
    image_filename = db.Column(db.String(100), nullable=True)

    # add a foreign key to the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('books', lazy=True))


    def get_average_rating(self):
        ratings = [r.rating for r in self.ratings]
        if len(ratings) > 0:
            return sum(ratings) / len(ratings)
        else:
            return None

    def get_average_rating_2(self):
        if len(self.rating) == 0:
            return 0
        else:
            sum = 0
            for rating in self.rating:
                sum += rating.stars
            return sum / len(self.rating)

    def get_all_ratings(self):
        return self.ratings.all()

    def __str__(self):
        return f'{self.title} {self.author}'

    def __repr__(self):
        return f'<Book {self.id} {self.title}'


class BookRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('ratings', lazy=True))
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))


class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(220), nullable=True)
    photo_filename = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


@manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))