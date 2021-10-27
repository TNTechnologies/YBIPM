from dominate.util import lazy
from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_nav import Nav
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Ye5xSCXkN2ROj2bn5FuV'
nav = Nav(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
admin = Admin(app, name='PMDatabase', template_mode='bootstrap3')


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


# TODO: Setup Flask Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = Users.query.filter_by(name=form.name.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html', form=form)

# Database models
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)


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

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text(40))
    description = db.Column(db.Text(100))
    pm_interval = db.Column(db.Integer)
    assets = db.relationship("Asset", backref='category')


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.Text(10))
    next_pm = db.Column(db.DateTime, default=datetime.datetime.now)
    description = db.Column(db.Text(40))
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text(255))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    failures = db.relationship('Failure', backref='asset')
    repairs = db.relationship('Repair', backref='asset')
    pms = db.relationship('PM', backref='asset')

    def __repr__(self):
        return '<Asset %r>' % self.id

class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("asset.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    reported_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100), nullable=False)
    notes = db.Column(db.Text(1024))
    completed = db.Column(db.Boolean)
    repairs = db.relationship('Repair', backref='failure')

    def __repr__(self):
        return '<Failure %r' % self.id

class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    category_id = db.Column(db.Integer, db.ForeignKey("failure.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    repaired_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100))
    notes = db.Column(db.Text(1024))
    completed = db.Column(db.Boolean)

    def __repr__(self):
        return '<Repair %r>' % self.id

class PM(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    performed_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100))
    notes = db.Column(db.Text(1024))

    def __repr__(self):
        return '<PM %r>' % self.id




#init_app
@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)

#@login_required
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Asset, db.session))
admin.add_view(ModelView(Failure, db.session))
admin.add_view(ModelView(Repair, db.session))
admin.add_view(ModelView(PM, db.session))

if __name__ == '__main__':
    db.init_app(app)
    db.create_all()
    app.run(debug=True)