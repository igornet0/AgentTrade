from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .models import *
import pandas as pd
import os

from . import db, login_manager, Api_model, TradingAgent, DatasetTimeseries
from .tasks import long_running_task
from datetime import datetime

from .handler import Handler
from random import randint

main = Blueprint('main', __name__)

def process_csv(file_path, df=None):
    if df is None:
        df = pd.read_csv(file_path)

    return {
        'filename': os.path.basename(file_path),
        'record_count': len(df),
        'preview': df.head().to_dict(orient='records')  # Превью первых 5 строк
    }
    
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

@main.route('/upload', methods=['POST'])
def upload():
    results = []
    
    if 'file' not in request.files:
        return jsonify({'error': "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        # Обработка одного файла
        file_path = os.path.join('uploads', file.filename)
        try:
            if file.filename in os.listdir('uploads'):
                dataset = DatasetTimeseries(file_path, path_save="uploads", file_name=file.filename)
                file_path_tmp = os.path.join('uploads_tmp', file.filename)
                file.save(file_path_tmp)
                datasetTMP = DatasetTimeseries(file_path_tmp, save=False)
                dataset.concat_dataset(datasetTMP)
                os.remove(file_path_tmp)
            else:
                file.save(file_path)
                dataset = DatasetTimeseries(file_path, path_save="uploads", 
                                            file_name=file.filename)
                dataset.process()
        except Exception as e:
            return jsonify({'error': f"{e}"}), 400

        result = process_csv(file_path, dataset.get_dataset())
        results.append(result)
        
    elif 'folder' in request.form:
        # Обработка папки
        folder_path = request.form['folder']
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(folder_path, filename)
                    results.append(process_csv(file_path))
        else:
            return jsonify({'error': "Invalid folder path"}), 400

    return jsonify(results)


@main.route('/start_parser', methods=['POST'])
@login_required
def start_parser():
    ticket = Ticket.query


@main.route('/start_train', methods=['POST'])
@login_required
def start_train():
    URL = request.form.get('URL')
    agents = Agent.query.filter_by(user_id=current_user.id).all()
    api = Api_model([TradingAgent(agent.path_agent, agent.balance) for agent in agents])
    
    # Запускаем задачу через Celery
    task = long_running_task.delay(agents)

    return jsonify({"message": "Task started", "celery_task_id": task.id}), 200
    handler = Handler(URL, api)
    handler.start_train(datetime.now())

    return "OK", 200

# Функция для получения данных из БД
def fetch_data_from_db(task_id):
    # Пример запроса из SQLite (замените на вашу БД)
    conn = sqlite3.connect("example.db")  # Укажите свою БД
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    # Преобразуем данные в словарь (замените под структуру своей БД)
    if row:
        return {"id": row[0], "data": row[1]}
    return None


# Маршрут для запуска задачи
@main.route('/start-process', methods=['POST'])
def start_process():
    data = request.get_json()
    task_id = data.get('task_id')

    if not task_id:
        return jsonify({"error": "Task ID is required"}), 400

    # Получаем данные из БД
    db_args = fetch_data_from_db(task_id)
    if not db_args:
        return jsonify({"error": "Task not found"}), 404

    # Запускаем задачу через Celery
    task = long_running_task.delay(db_args)

    return jsonify({"message": "Task started", "celery_task_id": task.id}), 200


# Маршрут для проверки статуса задачи
@main.route('/process-status/<celery_task_id>', methods=['GET'])
def get_process_status(celery_task_id):
    from celery.result import AsyncResult
    result = AsyncResult(celery_task_id)
    response = {"celery_task_id": celery_task_id, "status": result.state}
    if result.state == 'SUCCESS':
        response.update(result=result.result)
    elif result.state == 'FAILURE':
        response.update(error=str(result.result))
    return jsonify(response)