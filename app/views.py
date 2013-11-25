import json
from app import app
from flask import render_template, flash, redirect, request, session, g, url_for, make_response
from forms import SearchForm
from weibo import APIClient
# import initclient

APP_KEY = '3303493577'
APP_SECRET = '631caefd8ab03c1a4ddcf04e81e5a481'
CALLBACK_URL = 'http://127.0.0.1:5000/index'

@app.before_request
def before_request():
  g.client = None
  g.uid = None

  client = _create_client()

  code = request.args.get('code')
  if code and 'access_token' not in session:
    r = client.request_access_token(code)
    client.set_access_token(r.access_token, r.expires_in)
    session['expires_in'] = r.expires_in
    session['access_token'] = r.access_token
    session['uid'] = r.uid
    g.client = client
    g.uid = r.uid
  elif 'access_token' in session:
    client.set_access_token(session['access_token'], session['expires_in'])
    g.client = client
    g.uid = session['uid']

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index.html', methods = ['GET', 'POST'])
def index():
  # if cancel the authorized, redirect to /index
  # if session don't have access_token, that means you haven't logged in, redirect to /index
  if request.args.get('error') == 'access_denied' or g.client is None:
    return redirect(url_for('login'))

  users = g.client.users.show.get(uid = g.uid)
  json_users = json.dumps(users)
  dict_users = json.loads(json_users)
  friends = g.client.friendships.friends.get(uid = g.uid, count = 10)
  dict_friends = json.loads(json.dumps(friends))

  form = SearchForm()
  return render_template('index.html', title = 'index', users = dict_users, friends = dict_friends['users'], form = form)

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
  client = _create_client()
  url = client.get_authorize_url()
  return redirect(url)

@app.route('/signout')
def signout():
  session.pop('access_token', None)
  session.pop('expires_in', None)
  session.pop('uid', None)
  return redirect(url_for('login'))

@app.route('/error')
@app.route('/error.html')
def error():
  return render_template('error.html')

@app.route('/map')
@app.route('/map.html')
def getMap():
  return render_template('/map.html')

@app.route('/test')
def test():
  if 'access_token' not in session:
    print 'you cannot get in, redirect to index'
    return redirect(url_for('index'))
  else:
    print 'shit!!!'
    return 'holy shit'

def _create_client():
  return APIClient(APP_KEY, APP_SECRET, CALLBACK_URL)
