import json
from instagram.client import InstagramAPI
from app import app
from flask import render_template, flash, redirect, request, session, g, url_for, make_response
#from forms import SearchForm

CLIENT_ID = 'e3e18c92b35e4c3d82f6cfdfadc181e0'
CLIENT_SECRET = '0eb2ca3948af4398848570f099da8014'
REDIRECT_URI = 'http://127.0.0.1:5000/index'

@app.before_request
def before_request():
  g.api = None
  g.user = None

  code = request.args.get('code')
  if code and 'access_token' not in session:
    api = InstagramAPI(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI)
    access_token = api.exchange_code_for_access_token(code)
    session['access_token'] = access_token
    dict_access_token = json.loads(json.dumps(session['access_token']))
    g.api = InstagramAPI(access_token = dict_access_token[0])
    g.user = dict_access_token[1]
  elif 'access_token' in session:
    dict_access_token = json.loads(json.dumps(session['access_token']))
    g.api = InstagramAPI(access_token = dict_access_token[0])
    g.user = dict_access_token[1]

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index.html', methods = ['GET', 'POST'])
def index():
  #if cancel the authorized, redirect to /index
  #if g.user is none, that means you haven't logged in, redirect to /index
  if request.args.get('error') == 'access_denied' or g.user is None:
    return redirect(url_for('login'))

  if request.method == 'POST':
    if 'uid' in request.form:
      uid = request.form['uid']
      print 'uid: ', uid
      medias, next = g.api.user_recent_media(user_id = uid, count = 5)
      return generateJsonMedias(medias)
    elif 'lat' in request.form:
      lat = request.form['lat']
      lng = request.form['lng']
      return generateLocationMedias(lat, lng, 14)
    elif 'next' in request.form:
      # generate next follows page
      friends_cursor_list = session['friends_cursor_list']
      return json.dumps(generateFollows(friends_cursor_list, True))
    elif 'prev' in request.form:
      # generate prev follows page
      friends_cursor_list = session['friends_cursor_list']
      return json.dumps(generateFollows(friends_cursor_list, False))

  friends_cursor_list = []
  print 'user id: ', g.user['id']
  user = g.api.user(user_id = g.user['id'])
  follows = generateFollows(friends_cursor_list, True, 6)

  return render_template('index.html', title = 'index', user = user, follows = follows, logout = True)

def generateFollows(friends_cursor_list, doNext, count = 6):
  if doNext:
    # request for next follows page
    if len(friends_cursor_list) == 0:
      follows, follows_next = g.api.user_follows(user_id = g.user['id'], count = count)
    else:
      follows, follows_next = g.api.user_follows(next_url = friends_cursor_list[-1])

    if follows_next is None:
      print 'no next'
      has_next = False
      friends_cursor_list.append(False)
    else:
      has_next = True
      friends_cursor_list.append(follows_next)

    follows = addFlagToFollows(follows, has_next, True)
    print 'list size: ', len(friends_cursor_list)
    session['friends_cursor_list'] = friends_cursor_list
    return follows
  else:
    # request for prev follows page
    if len(friends_cursor_list) > 2:
      follows, follows_next = g.api.user_follows(next_url = friends_cursor_list[-3])
      has_prev = True
    elif len(friends_cursor_list) == 2:
      follows, follows_next = g.api.user_follows(user_id = g.user['id'], count = count)
      has_prev = False

    del friends_cursor_list[-1]
    follows = addFlagToFollows(follows, True, has_prev)
    print 'list size: ', len(friends_cursor_list)
    session['friends_cursor_list'] = friends_cursor_list
    return follows


def addFlagToFollows(follows, has_next, has_prev):
  json_follows = {}
  json_follows['follows'] = follows
  json_follows['hasNext'] = has_next
  json_follows['hasPrev'] = has_prev
  return json_follows

def generateLocationMedias(lat, lng, count):
  json_response = {}
  medias = g.api.media_search(q = 5000, count = count, lat = lat, lng = lng)
  i = 0
  for media in medias:
    json_response[i] = media
    i += 1

  json_response['count'] = len(json_response)
  return json.dumps(json_response)

def generateJsonMedias(medias):
  json_response = {}
  i = 0
  for media in medias:
    if media['location'] is not None and 'latitude' in media['location']:
      json_response[i] = media
      i += 1

  #print 'found %s medias with location' % len(json_response)
  json_response['count'] = len(json_response)
  #print 'json-response: ', json.dumps(json_response, sort_keys = False, indent = 2)
  return json.dumps(json_response)

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
  return render_template('login.html', title='Login', logout = False)

@app.route('/signin')
def signin():
  url = 'https://api.instagram.com/oauth/authorize/?client_id={0}&redirect_uri={1}&response_type=code'.format(CLIENT_ID, REDIRECT_URI)
  return redirect(url)

@app.route('/signout')
def signout():
  session.pop('access_token', None)
  return redirect(url_for('login'))

@app.route('/error')
@app.route('/error.html')
def error():
  return render_template('error.html')

@app.route('/map')
@app.route('/map.html')
def getMap():
  return render_template('/map.html')

def getToken(code):
  api = InstagramAPI(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI)
  access_token = api.exchange_code_for_access_token(code)
  return access_token
