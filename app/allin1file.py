from __future__ import absolute_import
from flask import Flask, render_template, request, redirect, url_for

import re
import urllib

from celery import Celery, chord

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

celery = make_celery(app)

URL_LIST = ['http://www.tacoma.uw.edu/faculty-assembly/contact-us',
			'http://www.emailtextmessages.com/',
			'http://www.google.com/',
			'http://www.google.com/',
			'http://www.google.com/',
			'http://www.google.com/']

@celery.task(name="tasks.add")
def add(x, y):
    return x + y

@celery.task(name="tasks.mul")
def mul(x, y):
    return x * y

@celery.task(name="tasks.xsum")
def xsum(numbers):
    return sum(numbers)

@celery.task(name="tasks.collectAllEmail")
def collectAllEmail(htmlSource):
	print('Collecting email from source.')
	email_pattern = re.compile("[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z]+[\.-0-9a-zA-Z]*\.[a-zA-Z]+")
	found_emails = re.findall(email_pattern, htmlSource)
	return found_emails

@celery.task(name="tasks.urlopen")
def urlopen(url):
	print('Opening: {0}'.format(url))
	try:
		socket = urllib.urlopen(url)
		html = socket.read()
		socket.close()
		return html
	except Exception as exc:
		socket.close()
		print('URL {0} gave error: {1!r}'.format(url, exc))

@app.route('/')
def main_view():
	# results = []
	# for url in URL_LIST:
	# 	body = urlopen.delay(url).get()
	# 	emails = collectAllEmail.delay(body).get()
	# 	results.append(emails)

	# return render_template('home.html', results=results)
	return render_template('home.html')


@app.route('/emails', methods=['GET', 'POST'])
def show_emails():
	if request.method == 'POST':
		url = request.form['url']
		body = urlopen.delay(url).get()
		emails = collectAllEmail.delay(body).get()
		return render_template('emails.html', emails=emails, count=len(emails))
	else:
		return redirect(url_for('main_view'))



if __name__ == '__main__':
    app.run(debug=True)