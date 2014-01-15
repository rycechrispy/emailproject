import re
import urllib
from config import make_celery, app

celery = make_celery(app)

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