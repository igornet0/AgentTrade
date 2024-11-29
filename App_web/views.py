from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from .models import *
from . import db, login_manager, Api_model, TradingAgent, Dataset

from datetime import datetime

from .handler import Handler
from flask_login import login_user, logout_user, login_required, current_user
from random import randint

main = Blueprint('main', __name__)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_page'))  # Перенаправить на главную страницу для залогиненных пользователей
    return render_template('login.html')

@main.route('/user_page')
@login_required
def user_page():
    data = Agent.query.filter_by(id_user=current_user.id).all()

    return render_template('user_page.html', username=current_user.username, data=data if data else False)

@main.route('/add_agent', methods=['POST'])
@main.route('/add_agents', methods=['POST'])
@login_required
def add_agent():
    agent_number = request.form.get('agent_number')

    if not agent_number:
        agent_number = 1

    user_id = current_user.id

    for i in range(int(agent_number)):
        Agent(name=f'Agent {i+1}', id_user=user_id, balance=randint(100, 100000), path_agent=f'Agents/user_{user_id}/agent_{i+1}')

    return redirect(url_for('main.user_page'))

@main.route('/start_train', methods=['POST'])
@login_required
def start_trade():
    URL = request.form.get('URL')
    agents = Agent.query.filter_by(id_user=current_user.id).all()
    api = Api_model([TradingAgent(agent.path_agent, agent.balance) for agent in agents])

    handler = Handler(URL, api)
    handler.start_train(datetime.now())

    return jsonify({"message": "Трейд запущен"}), 200

@main.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Имя файла пустое"}), 400

    # Проверяем, что это CSV файл
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Поддерживаются только CSV файлы"}), 400

    try:
        # Читаем CSV файл в DataFrame
        df = Dataset(file, save=False, search=False)
        if "coin" in file.filename:
            data = df.get_dataset()
            for value in data['coins']:
                if Stock.query.filter_by(name=value).first():
                    continue
                Stock(name=value, price_now=0, status_parser="new")

        return jsonify({"message": "Файл успешно загружен"}), 200
    except Exception as e:
        return jsonify({"error": f"Ошибка при обработке файла: {str(e)}"}), 500

# @main.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return app.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@main.route('/start_parser', methods=['POST'])
def start_parser():
    url = request.form.get('url')
    if "kucoin" in url:
        coins = Stock.query.all()
        parser_kucoin()
    return jsonify({"message": "Парсинг запущен"}), 200