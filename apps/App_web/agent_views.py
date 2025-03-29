from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import *
from . import db
from flask_login import login_user, logout_user

bp = Blueprint('agent', __name__)

@bp.route("/<int:agent_id>", methods=['GET', 'POST'])
def get_agent(agent_id):
    agent = Agent.query.filter_by(id=agent_id).first()
    transaction = Transaction.query.filter_by(agent_id=agent_id).all()
    return render_template('agent_page.html', agent=agent, transaction=transaction)