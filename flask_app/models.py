from flask_login import UserMixin
from . import db, login_manager
from . import config
import base64
import pyotp


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    otp_secret = db.StringField(required=True, min_length=16, max_length=16, default=pyotp.random_base32())


    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    class_name = db.StringField(required=True, min_length=1, max_length=100)
    notes_title = db.StringField(required=True, min_length=1, max_length=100)
    notes_id = db.StringField(required=True)
    rating = db.IntField(required=True, min=1, max=5)

class Notes(db.Document):
    notetaker = db.ReferenceField(User, required=True)
    title = db.StringField(required=True, min_length=1, max_length=100)
    class_name = db.StringField(required=True, min_length=1, max_length=100)
    date = db.StringField(required=True)
    notes_file = db.FileField(required=False)

    # Returns unique string identifying our object
    def get_id(self):
        return str(self.id)
