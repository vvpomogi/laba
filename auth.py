from flask import render_template, Blueprint, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from db import User
from werkzeug.security import generate_password_hash

auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    return redirect(url_for('auth.login'))


@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    else:
        return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.get_or_none(email=email)
    if not user or not user.authenticate(password):
        flash('<p class="notification is-danger">Please check your login details and try again.</p>')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    number = request.form.get('number')
    user = User.get_or_none(email=email)
    if user:
        flash('<p class="notification is-danger">Email address already exists. Go to <a href="login">login page</a></p>')
        return redirect(url_for('auth.signup'))
    User.create(email=email, password=generate_password_hash(password, method='pbkdf2'), number=number)
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))
