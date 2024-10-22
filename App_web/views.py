from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from .models import *
from . import db, login_manager, Api_model, TradingAgent

from datetime import datetime

from .handler import Handler
from flask_login import login_user, logout_user, login_required, current_user
from random import randint

main = Blueprint('main', __name__)
    
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_page'))  # Перенаправить на главную страницу для залогиненных пользователей
    return render_template('login.html')

@main.route('/user_page')
@login_required
def user_page():
    data = Agent.query.filter_by(user_id=current_user.id).all()

    return render_template('user_page.html', username=current_user.username, data=data if data else False)

@main.route('/add_agent', methods=['POST'])
@login_required
def add_agent():
    agent_number = request.form.get('agent_number')
    user_id = current_user.id
    for i in range(int(agent_number)):
        agent = Agent(name=f'Agent {i+1}', user_id=user_id, balance=randint(100, 100000), path_agent=f'Agents/agent_{i+1}')

    return "OK", 200


@main.route('/start_train', methods=['POST'])
@login_required
def start_trade():
    URL = request.form.get('URL')
    agents = Agent.query.filter_by(user_id=current_user.id).all()
    api = Api_model([TradingAgent(agent.path_agent, agent.balance) for agent in agents])

    handler = Handler(URL, api)
    handler.start_train(datetime.now())

    return "OK", 200


