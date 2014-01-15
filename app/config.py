from __future__ import absolute_import
from flask import Flask
from celery import Celery

app = Flask(__name__)
app.secret_key = "gk_-+x6q@c)hf*w)bh0t#fh7)mz3liy=*godtwl#3fj%&7eg6(xxxx"
app.config.update(
		CELERY_BROKER_URL='amqp://guest@localhost//',
    	CELERY_RESULT_BACKEND='amqp://',
    	CELERY_TASK_RESULT_EXPIRES=3600
	)

def make_celery(app):
    celery = Celery(app.import_name, 
    				broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery