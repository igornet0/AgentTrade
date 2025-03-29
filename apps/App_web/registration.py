from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import *
from . import db
from flask_login import login_user

bp = Blueprint('register', __name__)

@bp.route("/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        user = User(username=username, password=password)

        login_user(user)
        flash('Your account has been created! You are now able to log in', 'success')

        return redirect(url_for('main.user_page'))
    
    return render_template('register.html')