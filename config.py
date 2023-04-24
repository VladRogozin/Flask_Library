import os
from os import getenv

from dotenv import load_dotenv


load_dotenv()


def idea():
    from Flask_Library.application import app
    return app


class Config:
    SECRET_KEY = getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOK_UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/uploads/book'
    IMAGE_UPLOAD_FOLDER = os.path.join(idea().root_path, 'static', 'images')
    IMAGE_PROFILE_FOLDER = os.path.join(idea().root_path, 'static', 'profile')
    ALLOWED_EXTENSIONS = {'pdf', 'epub'}
