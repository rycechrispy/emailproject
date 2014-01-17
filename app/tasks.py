import re
import urllib
from config import make_celery, app
from celery import Task

celery = make_celery(app)

@celery.task(name="tasks.get_emails")
def get_emails(htmlSource):
	print('Collecting email from source.')
	try:
		email_pattern = re.compile("[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z]+[\.-0-9a-zA-Z]*\.[a-zA-Z]+")
		found_emails = re.findall(email_pattern, htmlSource)
		unique_emails = list(set(found_emails))
		return unique_emails
	except Exception as exc:
		print('htmlSource {0} gave error: {1!r}'.format(htmlSource, exc))
	# return found_emails

@celery.task(name="tasks.urlopen")
def urlopen(url):
	#some things to look out for: 
	# - should i retry for links that might be dead? timeout
	# - getting poop input screws up getting emails, what should i do?
	# - 
	print('Opening: {0}'.format(url))
	try:
		socket = urllib.urlopen(url)
		html = socket.read()
		socket.close()
		return html
	except Exception as exc:
		print('URL {0} gave error: {1!r}'.format(url, exc))

class UrlOpenJob(Task):
	def run(self, url):
		print('Opening: {0}'.format(url))
		try:
			socket = urllib.urlopen(url)
			html = socket.read()
			socket.close()
			return html
		except Exception as exc:
 			print('URL {0} gave error: {1!r}'.format(url, exc))

 	def on_success(self, retval, task_id, args, kwargs):
		GetEmailsJob().delay(retval)

class GetEmailsJob(Task):
	def run(self, htmlSource):
		print('Collecting email from source.')
		try:
			email_pattern = re.compile("[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z]+[\.-0-9a-zA-Z]*\.[a-zA-Z]+")
			found_emails = re.findall(email_pattern, htmlSource)
			unique_emails = list(set(found_emails))
			return unique_emails
		except Exception as exc:
			print('htmlSource {0} gave error: {1!r}'.format(htmlSource, exc))
