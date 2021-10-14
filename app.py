from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_nav import Nav
from forms import LoginForm
from models import *
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib import sqla as flask_admin_sqla
from flask_admin import AdminIndexView
from flask_admin import expose
from flask_admin.menu import MenuLink

app = Flask(__name__)
nav = Nav(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# TODO SQL Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.secret_key = 'Ye5xSCXkN2ROj2bn5FuV'


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

@login_manager.user_loader
def load_user(id):
    return Users.get(int(id))

if __name__ == '__main__':
    db.init_app(app)
    db.create_all()
    app.run(debug=True)