from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import *
from . import db
from flask_login import login_user, logout_user

bp = Blueprint('login', __name__)

@bp.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('main.user_page'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html')

@bp.route("/logout", methods=['POST'])
def logout():
    logout_user()
    return render_template('login.html')