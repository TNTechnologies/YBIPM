import asset as asset
import flask_sqlalchemy
from dominate.util import lazy
from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Separator, Subgroup, Link
from sqlalchemy import ForeignKey, false
from sqlalchemy.orm import relationship, backref
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

#App setup and configurable
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
bc = Breadcrumbs(app)
migrate = Migrate(app, db)

#Navbar
@nav.navigation()
def ybinavbar():
    return Navbar(
        'YBI Geo',
        View('Home', 'index'),
        View('Tool', 'category', type='tool'),
        View('Equipment', 'category', type='equipment'),
        View('Truck', 'category', type='truck'),
        View('Logout', 'logout')

    )


#Routes
@app.route('/')
@login_required
@register_breadcrumb(app, '.', 'Home')
def index():  # put application's code here
    return render_template('index.html')

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

@app.route('/category/<type>')
@login_required
def category(type):
    query = Category.query.filter_by(type=type).all()
    return render_template('category_list.html', query=query)


@app.route('/failure/<int:id>')
@login_required
def failure(id):
    return render_template('event_report.html')

@app.route('/repair/<int:id>')
@login_required
def repair(id):
    return render_template('event_report.html')

@app.route('/pm/<int:id>', methods=['GET', 'POST'])
@login_required
def pm(id):
    asset = Asset.query.filter_by(id=id).first()
    cat = Category.query.filter_by(id=asset.category_id).first()
    form = PMReport()
    if request.method == 'POST':

        asset.next_pm = datetime.datetime.today() + datetime.timedelta(days=cat.pm_interval)
        pm = PM(notes=form.notes.data, performed_by=current_user.name, asset_id=id, description=form.description.data)
        db.session.add(pm)
        db.session.commit()
        return redirect(url_for('asset', id=id))
    return render_template('pm_report.html', form=form, asset=asset)

@app.route('/asset/<int:id>')
@login_required
def asset(id):
    asset = Asset.query.filter_by(id=id).first()
    failures = Failure.query.filter_by(asset_id=id).all()
    repairs = Repair.query.filter_by(asset_id=id).all()
    pms = PM.query.filter_by(asset_id=id).all()

    return render_template('asset_view.html', asset=asset, failures=failures, pms=pms, repairs=repairs)

@app.route('/asset_list/<int:id>')
def asset_list(id):
   query = Asset.query.filter_by(category_id=id).all()
   return render_template('asset_list.html', query=query)


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
    type = db.Column(db.Text(20), nullable=False)
    pm_interval = db.Column(db.Integer, default=0)
    assets = db.relationship("Asset", backref='category')

    def __repr__(self):
        return self.name

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
        return self.serial_number

class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("asset.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    reported_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100), nullable=False)
    notes = db.Column(db.Text(1024), nullable=False)
    completed = db.Column(db.Boolean)
    repairs = db.relationship('Repair', backref='failure')

    def __repr__(self):
        return str(self.id)

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
        return str(self.id)

class PM(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    performed_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100))
    notes = db.Column(db.Text(1024))

    def __repr__(self):
        return str(self.id)


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
            ('tool', 'Tool'),
            ('equipment', 'Equipment'),
            ('truck', 'Truck')
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
    edit_modal = True
    create_modal = True

class RepairView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    create_modal = True
    edit_modal = True

class PMView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    create_modal = True
    edit_modal = True

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
