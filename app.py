from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Separator, Subgroup, Link
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
        View('Admin', 'admin.index'),
        View('Logout', 'logout')

    )


#Routes
@app.route('/')
@login_required
def index():  # put application's code here
    assets = Asset.query.filter(Asset.next_pm <= datetime.datetime.now() + datetime.timedelta(days=7)).all()
    failures = Failure.query.filter_by(completed=False).all()
    return render_template('index.html',
                           assets=assets,
                           failures=failures)

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


@app.route('/failure_report/<int:id>', methods=['GET', 'POST'])
@login_required
def failure_report(id):
    form = FailureReport()
    asset = Asset.query.filter_by(id=id).first()
    if request.method == 'POST':
        failure = Failure(description=form.description.data,
                          notes=form.notes.data,
                          date=datetime.datetime.now(),
                          reported_by=current_user.name,
                          asset_id=id)
        asset.active = False
        db.session.add(failure)
        db.session.commit()
        return redirect(url_for('asset', id=id))
    return render_template('failure_report.html',
                           asset=asset,
                           form=form)

@app.route('/failure/<int:id>', methods=['GET', 'POST'])
@login_required
def failure(id):
    failure = Failure.query.filter_by(id=id).first()
    asset = Asset.query.filter_by(id=failure.asset_id).first()
    repair = Repair.query.filter_by(id=failure.id).all()
    form = FailureReport(obj=failure)
    if request.method == 'POST':
        failure.description = form.description.data
        failure.notes = form.notes.data
        db.session.commit()
        return redirect(url_for('asset', id=failure.asset_id))
    return render_template('failure.html',
                           form=form,
                           failure=failure,
                           asset=asset,
                           repair=repair)

@app.route('/repair/<int:id>', methods=['GET', 'POST'])
@login_required
def repair(id):
    repair = Repair.query.filter_by(id=id).first()
    failure = Failure.query.filter_by(id=repair.failure_id).first()
    asset = Asset.query.filter_by(id=repair.asset_id).first()
    category = Category.query.filter_by(id=asset.category_id).first()
    form = RepairReport(obj=repair)
    if request.method == 'POST':
        repair.description = form.description.data
        repair.notes = form.notes.data
        repair.completed = form.completed.data
        if form.completed.data == True:
            failure.completed = True
            asset.active = True
            asset.next_pm = datetime.datetime.today() + datetime.timedelta(days=category.pm_interval)
        db.session.commit()
        return redirect(url_for('asset', id=asset.id))
    return render_template('repair.html',
                           form=form,
                           asset=asset,
                           failure=failure,
                           repair=repair)

@app.route('/repair_report/<int:id>', methods=['GET', 'POST'])
@login_required
def repair_report(id):
    failure = Failure.query.filter_by(id=id).first()
    asset = Asset.query.filter_by(id=failure.asset_id).first()
    category = Category.query.filter_by(id=asset.category_id).first()
    form = RepairReport()
    if request.method == 'POST':
        repair = Repair(repaired_by=current_user.name,
                        description=form.description.data,
                        notes=form.notes.data,
                        asset_id=asset.id,
                        failure_id=failure.id,
                        completed=form.completed.data)
        if form.completed.data == True:
            failure.completed = True
            asset.active = True
            asset.next_pm = datetime.datetime.now() + datetime.timedelta(days=category.pm_interval)
        db.session.add(repair)
        db.session.commit()
        return redirect(url_for('asset', id=repair.asset_id))
    return render_template('repair_report.html',
                           failure=failure,
                           asset=asset,
                           form=form)

@app.route('/pm/<int:id>', methods=['GET', 'POST'])
@login_required
def pm(id):
    asset = Asset.query.filter_by(id=id).first()
    cat = Category.query.filter_by(id=asset.category_id).first()
    form = PMReport()
    if request.method == 'POST':

        asset.next_pm = datetime.datetime.today() + datetime.timedelta(days=cat.pm_interval)
        pm = PM(notes=form.notes.data,
                performed_by=current_user.name,
                asset_id=id,
                description=form.description.data)
        db.session.add(pm)
        db.session.commit()
        return redirect(url_for('asset', id=id))
    return render_template('pm_report.html',
                           form=form,
                           asset=asset)

@app.route('/asset/<int:id>')
@login_required
def asset(id):
    asset = Asset.query.filter_by(id=id).first()
    failures = Failure.query.filter_by(asset_id=id).all()
    repairs = Repair.query.filter_by(asset_id=id).all()
    pms = PM.query.filter_by(asset_id=id).all()
    cals = Calibration.query.filter_by(asset_id=id).all()

    return render_template('asset_view.html',
                           asset=asset,
                           failures=failures,
                           pms=pms,
                           repairs=repairs,
                           cals=cals)

@app.route('/asset_list/<int:id>')
@login_required
def asset_list(id):
   query = Asset.query.filter_by(category_id=id).all()
   return render_template('asset_list.html',
                          query=query)

@app.route('/cal/<int:id>', methods=['GET', 'POST'])
@login_required
def calibrate(id):
    asset = Asset.query.filter_by(id=id).first()
    cat = Category.query.filter_by(id=asset.category_id).first()
    form = CalReport()
    if request.method == 'POST':
        asset.next_cal = datetime.datetime.today() + datetime.timedelta(days=cat.cal_interval)
        cal = Calibration(asset_id=id,
                          performed_by=current_user.name,
                          description=form.description.data,
                          values=form.values.data)
        db.session.add(cal)
        db.session.commit()
        return redirect(url_for('asset', id=id))
    return render_template('cal_report.html',
                           form=form,
                           asset=asset)

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
    cal_interval = db.Column(db.Integer, default=0)
    assets = db.relationship("Asset", backref='category')
    pm_procedure = db.Column(db.Text(1024))
    calibration_required = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.name

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_number = db.Column(db.Text(10))
    next_pm = db.Column(db.DateTime, default=datetime.datetime.now)
    next_cal = db.Column(db.DateTime, default=datetime.datetime.now)
    description = db.Column(db.Text(80))
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text(255))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    failures = db.relationship('Failure', backref='asset')
    repairs = db.relationship('Repair', backref='asset')
    pms = db.relationship('PM', backref='asset')
    cals = db.relationship('Calibration', backref='asset')

    def __repr__(self):
        return self.serial_number

class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("asset.id"))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    reported_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100), nullable=False)
    notes = db.Column(db.Text(1024), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    repairs = db.relationship('Repair', backref='failure')

    def __repr__(self):
        return str(self.id)

class Repair(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    failure_id = db.Column(db.Integer, db.ForeignKey("failure.id"))
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

class Calibration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    performed_by = db.Column(db.Text(20))
    description = db.Column(db.Text(100))
    values = db.Column(db.Text(1024))

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

class CalView(ModelView):
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
admin.add_view(CalView(Calibration, db.session))

if __name__ == '__main__':
    db.init_app(app)
    db.create_all()
    migrate.init_app(app)
    nav.init_app(app)
    app.run(debug=True)

