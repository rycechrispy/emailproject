from flask import render_template, request, redirect, url_for, Response
from config import app
from tasks import get_emails, urlopen, UrlOpenJob, GetEmailsJob
from celery import chain
import time

def stream_template(template_name, **context):
    # http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    # rv.enable_buffering(5)
    return rv

@app.route('/')
def main_view():
	return render_template('home.html')

@app.route('/emails', methods=['GET', 'POST'])
def show_emails():
	if request.method == 'POST':
		if request.form['options'] == 'url': # for URLs
			url = request.form['input'].strip()
			if ',' in url:
				url_list = url.split(",")
				def g():
					emails = []
					count = 0
					link_count = 0
					for url in url_list:
						emails_for_url = find_emails_from_url(url)
						emails.append(emails_for_url)
						count += len(emails_for_url)
						link_count = len(emails)
						yield emails_for_url, count, link_count, url
				return Response(stream_template('emails.html', data=g()))
				# count = 0
				# for url in url_list:
				# 	emails_for_url = find_emails_from_url(url)
				# 	emails.append(emails_for_url)
				# 	count += len(emails_for_url)
				# 	print emails_for_url
				# return render_template('emails.html', emails=emails, count=count, url_list=url_list, link_count=len(emails))
			elif ' ' in url:
				url_list = url.split(" ")
				emails = []
				count = 0
				for url in url_list:
					emails_for_url = find_emails_from_url(url)
					emails.append(emails_for_url)
					count += len(emails_for_url)
					print emails_for_url
				return render_template('emails.html', emails=emails, count=count, url_list=url_list, link_count=len(emails))
			else:
				# body = urlopen.delay(url).get()
				# emails = get_emails.delay(body).get()
				emails = find_emails_from_url(url)
				print emails
				return render_template('emails.html', emails=emails, count=len(emails), url=url, link_count=1)
		else: #for text only
			text = request.form['input']
			emails =  find_emails_from_text(text)
			return render_template('emails.html', emails=emails, count=len(emails), text=request.form['options'])
	else:
		return redirect(url_for('main_view'))


def find_emails_from_url(url):
	# chain = urlopen.s(url) | get_emails.s()
	# return chain().get()
	# body = urlopen.delay(url).get()
	# emails = get_emails.delay(body).get()
	body = UrlOpenJob().delay(url).get()
	emails = GetEmailsJob().delay(body).get()
	return emails

def find_emails_from_text(text):
	emails = GetEmailsJob().delay(text).get()
	return emails

if __name__ == '__main__':
    app.run(debug=True)