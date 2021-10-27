import flask_sqlalchemy
from dominate.util import lazy
from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from sqlalchemy import ForeignKey, false
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
admin = Admin(app, name='YBI Geo Admin', template_mode='bootstrap3')

#Navbar
@nav.navigation()
def ybinavbar():
    return Navbar(
        'YBI Geo',
        View('Home', 'index')

    )


#Routes
@app.route('/')
@login_required
def index():  # put application's code here
    tools = Category.query.filter_by(type='Tool').all()
    equipment = Category.query.filter_by(type='Equipment').all()
    trucks = Category.query.filter_by(type='Truck').all()
    return render_template('index.html', tools=tools, equipment=equipment, trucks=trucks)

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/failure')
@login_required
def failure():
    return render_template('failure_report.html')


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

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return '<Users %r>' % self.id

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text(40), nullable=False)
    description = db.Column(db.Text(100))
    type = db.Column(db.Text(20))
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


#Admin View modules
class UserView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    can_delete = True
    edit_modal = True
    create_modal = True
    column_exclude_list = ['password_hash']

class CategoryView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

    create_modal = True
    edit_modal = True
    form_choices = {
        'type':[
            ('TOOL', 'Tool'),
            ('EQUIPMENT', 'Equipment'),
            ('TRUCK', 'Truck')
        ]
    }

class AssetView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    create_modal = True
    edit_modal = True

class FailureView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class RepairView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class PMView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

#user loader !! Don't Mess with
@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)

#Admin View Structure
admin.add_view(UserView(Users, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(AssetView(Asset, db.session))
admin.add_view(FailureView(Failure, db.session))
admin.add_view(RepairView(Repair, db.session))
admin.add_view(PMView(PM, db.session))

if __name__ == '__main__':
    db.init_app(app)
    db.create_all()
    nav.init_app(app)
    app.run(debug=True)
