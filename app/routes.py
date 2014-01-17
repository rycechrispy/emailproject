from flask import render_template, request, redirect, url_for
from config import app
from tasks import get_emails, urlopen, UrlOpenJob, GetEmailsJob
from celery import chain

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
				emails = []
				count = 0
				for url in url_list:
					emails_for_url = find_emails_from_url(url)
					emails.append(emails_for_url)
					count += len(emails_for_url)
					print emails_for_url
				return render_template('emails.html', emails=emails, count=count, url_list=url_list, link_count=len(emails))
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
				return render_template('emails.html', emails=emails, count=len(emails), url=url)
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