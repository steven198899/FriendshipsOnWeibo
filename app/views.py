import json
from app import app
from flask import render_template, flash, redirect, request, session, g, url_for, make_response
from forms import SearchForm
from weibo import APIClient
# import initclient

APP_KEY = '3303493577'
APP_SECRET = '631caefd8ab03c1a4ddcf04e81e5a481'
CALLBACK_URL = 'http://127.0.0.1:5000/index'

#@app.before_request
#def before_request():
  #g.client = None

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index.html', methods = ['GET', 'POST'])
def index():
  # if cancel the authorized, redirect to ./login
  if request.args.get('error') == 'access_denied':
    return redirect(url_for('login'))

  if 'access_token' in session:
    client = _create_client()
    client.set_access_token(session['access_token'], session['expires_in'])
    users = client.users.show.get(uid="2199734770")
    json_users = json.dumps(users)
    dict_users = json.loads(json_users)
    friends = client.friendships.friends.get(uid="2199734770", count=10)
    dict_friends=json.loads(json.dumps(friends))

    form = SearchForm()
    if form.validate_on_submit():
      return searchResult(form.searchName.data)
    # return render_template('index.html', title='Home', form=form)
    return render_template('searchResult.html', title="Index", users=dict_users, friends=dict_friends['users'], form=form)
  else:
    code = request.args.get('code')
    if code:
      client = _create_client()
      r = client.request_access_token(code)
      client.set_access_token(r.access_token, r.expires_in)
      session['expires_in']=r.expires_in
      session['access_token'] = r.access_token
      form = SearchForm()
      return render_template('index.html', title='Home', form=form)
    else:
      return redirect(url_for('login'))


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
  return redirect(url_for('login'))

@app.route('/error')
@app.route('/error.html')
def error():
  return render_template('error.html')

@app.route('/searchResult')
@app.route('/searchResult.html')
def searchResult(searchName):
  screen_name="Steven"
  #img_logo="http://tp3.sinaimg.cn/2199734770/180/40018321658/1"
  img_logo="https://pbs.twimg.com/profile_images/1799277908/7efdd96e-252e-4195-9e61-f1d8ca595630_bigger.jpg"
  friends_count=163
  followers_count=877
  statuses_count=999
  form=SearchForm()
  # searchName=searchName
  # flash('Searching: '+ searchName)
  return render_template('searchResult.html', title=screen_name, img_logo=img_logo,
    screen_name=screen_name, friends_count=friends_count, followers_count=followers_count,
    statuses_count=statuses_count, form=form)

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
