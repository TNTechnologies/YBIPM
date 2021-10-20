from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text(255), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('Category.id'))
    notes = db.Column(db.Text(1024), nullable=False)
    active = db.Column(db.Boolean, default=True)
    models = db.Column(db.Text(80), nullable=False)
    next_pm = db.Column(db.DateTime)
    
    def __repr__(self):
        return '<Tools %r>' % self.id


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text(255), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('Category.id'))
    notes = db.Column(db.Text(1024), nullable=False)
    active = db.Column(db.Boolean, default=True)
    next_pm = db.Column(db.DateTime)
    
    def __repr__(self):
        return '<Equipment %r>' % self.id


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text(255), nullable=False)
    notes = db.Column(db.Text(1024), nullable=False)
    
    def __repr__(self):
        return '<Category %r>' % self.id

class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    user = db.Column(db.Integer, db.ForeignKey('User.id'))
    asset_id = db.Column(db.Integer, db.ForeignKey('Tools.id'))
    description = db.Column(db.Text(255), nullable=False)
    notes = db.Column(db.Text(1024), nullable=False)
    
    def __repr__(self):
        return '<Failure %r>' % self.id

class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('Tools.id'))
    user = db.Column(db.Integer, db.ForeignKey('Users.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.Text(255), nullable=False)
    notes = db.Column(db.Text(1024))
    
    def __repr__(self):
        return '<Repair %r>' % self.id


class Pm(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('Tools.id'))
    user = db.Column(db.Integer, db.ForeignKey('Users.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    
    def __repr__(self):
        return '<Pm %r>' % self.id


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

    def __repr__(self):
        return '<Users %r>' % self.id