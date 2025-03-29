from celery import Celery

# Создаём экземпляр Celery
celery_app = Celery(
    'tasks',
    broker='pyamqp://guest:guest@localhost//',  # RabbitMQ как брокер
    backend='redis://localhost:6379/0'         # Redis для хранения результатов
)

# Настройки Celery
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,  # Результаты хранятся 1 час
    timezone='UTC',
    enable_utc=True
)
