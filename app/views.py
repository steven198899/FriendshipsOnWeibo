from app import app
from flask import render_template, flash, redirect, request, session
from forms import SearchForm
from weibo import APIClient
# import initclient

APP_KEY = '3303493577'
APP_SECRET = '631caefd8ab03c1a4ddcf04e81e5a481'
CALLBACK_URL = 'http://127.0.0.1:5000/index'

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index.html', methods = ['GET', 'POST'])
def index():
	# if cancel the authorized, redirect to ./login
	if request.args.get('error') == 'access_denied':
		return redirect('/login')

	# get the code and save the token
	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
	code = request.args.get('code')
	if code:
		if 'access_token' not in session:
			r = client.request_access_token(code)
			session['access_token'] = r.access_token

	if 'access_token' in session:
		form=SearchForm()
		if form.validate_on_submit():
		# flash('Hello! '+ form.searchName.data)
			return searchResult(form.searchName.data)
			# return signout()
		# return redirect('/searchResult')
		return render_template('index.html', title='Home', form=form)
	else:
		return redirect('/login')

@app.route('/description')
@app.route('/description.html')
def getDesc():
	return render_template('description.html')

@app.route('/team')
@app.route('/team.html')
def getTeam():
	return render_template('team.html')

@app.route('/login')
@app.route('/login.html')
def login():
	return render_template('login.html', title='Login')

@app.route('/signin')
def signin():
	client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
	url = client.get_authorize_url()
	return redirect(url)

@app.route('/signout')
def signout():
	print "--------------"
	del session['access_token']	
	return redirect('/login')

@app.route('/error')
@app.route('/error.html')
def error():
	return render_template('error.html')

@app.route('/searchResult')
@app.route('/searchResult.html')
def searchResult(searchName):
	screen_name="Steven"
	img_logo="http://tp3.sinaimg.cn/2199734770/180/40018321658/1"
	friends_count=163
	followers_count=877
	statuses_count=999
	# searchName=searchName
	# flash('Searching: '+ searchName)
	return render_template('searchResult.html', title='searchResult', img_logo=img_logo, screen_name=screen_name, friends_count=friends_count, followers_count=followers_count, statuses_count=statuses_count)

@app.route('/map')
@app.route('/map.html')
def getMap():
	return render_template('/map.html')
