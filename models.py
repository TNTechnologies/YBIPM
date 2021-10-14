import datetime
from app import login_manager, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


#Database models
class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text(255), nullable=False)
    category = db.Column(db.Integer, foreign_keys='Category.id')
    notes = db.Column(db.Text(1024), nullable=False)
    active = db.Column(db.Boolean, default=True)
    models = db.Column(db.Text(80), nullable=False)
    next_pm = db.Column(db.DateTime)


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text(255), nullable=False)
    category = db.Column(db.Integer, foreign_keys='Category.id')
    notes = db.Column(db.Text(1024), nullable=False)
    active = db.Column(db.Boolean, default=True)
    next_pm = db.Column(db.DateTime)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text(255), nullable=False)
    notes = db.Column(db.Text(1024), nullable=False)


class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    user = db.Column(db.Integer, foreign_keys='User.id')
    asset_id = db.Column(db.Integer, foreign_keys='Tools.id')
    description = db.Column(db.Text(255), nullable=False)
    notes = db.Column(db.Text(1024), nullable=False)


class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, foreign_keys='Tools.id')
    user = db.Column(db.Integer, foreign_keys='Users.id')
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.Text(255), nullable=False)
    notes = db.Column(db.Text(1024))


class Pm(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, foreign_keys='Tools.id')
    user = db.Column(db.Integer, foreign_keys='Users.id')
    date = db.Column(db.DateTime, default=datetime.datetime.now())


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id