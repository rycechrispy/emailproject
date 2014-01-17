from __future__ import absolute_import
from flask import Flask
from celery import Celery
from kombu import Exchange, Queue

app = Flask(__name__)
app.secret_key = "gk_-+x6q@c)hf*w)bh0t#fh7)mz3liy=*godtwl#3fj%&7eg6(xxxx"
app.config.update(
        # BROKER_HOST = "localhost",
        # BROKER_PORT = 5672,
        # BROKER_VHOST = "/",
        # BROKER_USER = "guest",
        # BROKER_PASSWORD = "guest",
        # CELERY_IMPORTS = ('tasks'),

        # CELERY_BROKER_URL='amqp://guest@localhost//',
        # CELERY_RESULT_BACKEND='amqp://guest@localhost//',

        BROKER_HOST = "localhost",
        BROKER_PORT = 5672,
        BROKER_VHOST = "chrishost",
        BROKER_USER = "chris",
        BROKER_PASSWORD = "chris",
        CELERY_IMPORTS = ('tasks'),

        CELERY_BROKER_URL='amqp://chris:chris@localhost/chrishost',
        CELERY_RESULT_BACKEND='amqp://chris:chris@localhost/chrishost',

    	CELERY_TASK_RESULT_EXPIRES=3600,

        CELERY_DEFAULT_EXCHANGE = "default",
        CELERY_DEFAULT_EXCHANGE_TYPE = "direct",
        CELERY_DEFAULT_ROUTING_KEY = "task.default",

        CELERY_QUEUES = (
            Queue('urlopen', Exchange('urlopen'), routing_key='urlopen'),
            Queue('getemails', Exchange('getemails'), routing_key='getemails')
        ),
        CELERY_ROUTES = {
            'tasks.urlopen': {'queue': 'urlopen', 'routing_key': 'urlopen'},
            'tasks.get_emails': {'queue': 'getemails', 'routing_key': 'getemails'},
            'tasks.UrlOpenJob': {'queue': 'urlopen', 'routing_key': 'urlopen'},
            'tasks.GetEmailsJob': {'queue': 'getemails', 'routing_key': 'getemails'}
        }
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