import os

from celery import Celery

rabbitmq_address = os.getenv('RABBITMQ_ADDRESS')
if rabbitmq_address is None:
    rabbitmq_address = 'localhost'

rabbitmq_user = os.getenv('RABBITMQ_USER')
if rabbitmq_user is None:
    rabbitmq_user = 'guest'

rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
if rabbitmq_password is None:
    rabbitmq_password = 'guest'

rabbitmq_url = f'amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_address}:5672/'

celery_app = Celery(
    __name__,
    broker=rabbitmq_url,
    imports=('src.Background.sync_task',)
)

celery_app.conf.beat_schedule = {
    'sync_task': {
        'task': 'src.Background.sync_task.sync_task',
        'schedule': 15.0,
    },
}

celery_app.conf.timezone = 'UTC'
celery_app.autodiscover_tasks()
