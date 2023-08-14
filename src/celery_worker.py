from celery import Celery

# celery_app = Celery('worker', broker='amqp://guest:guest@localhost:5672/')
celery_app = Celery(
    __name__,
    broker='amqp://guest:guest@rabbitmq:5672/',
    # backend='amqp://guest:guest@localhost:5672/'
)
celery_app.conf.task_routes = {'app.worker.test_celery': 'main-queue'}
