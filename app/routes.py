from flask import render_template, request, redirect, url_for
from config import app
from tasks import collectAllEmail, urlopen

URL_LIST = ['http://www.tacoma.uw.edu/faculty-assembly/contact-us',
			'http://www.emailtextmessages.com/',
			'http://www.google.com/',
			'http://www.google.com/',
			'http://www.google.com/',
			'http://www.google.com/']

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