from App_web.celery_config import celery_app
import time

# Длительная задача
@celery_app.task(bind=True)
def long_running_task(self, db_args):
    task_id = db_args.get("id", "unknown")
    try:
        print(f"Задача {task_id} запущена с аргументами: {db_args}")
        time.sleep(10)  # Имитация длительной работы
        print(f"Задача {task_id} завершена")
        return {"status": "completed", "task_id": task_id}
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise e