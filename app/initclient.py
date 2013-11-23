#! /usr/bin/python

import weibo 
# import urllib
import time
import os


class myAPIClient(weibo.APIClient):
	def __init__(self, app_key, app_secret, redirect_uri=None, response_type='code', domain='api.weibo.com', version='2'):
		weibo.APIClient.__init__(self, app_key, app_secret, redirect_uri=redirect_uri, response_type='code', domain='api.weibo.com', version='2')
		self.uid = ""

	def request_access_token_info(self, at):
		'''
		return access token as a JsonDict: {"access_token":"your-access-token","expires_in":12345678,"uid":1234}, expires_in is represented using standard unix-epoch-time
		'''
		r = weibo._http_post('%s%s' % (self.auth_url, 'get_token_info'), access_token = at)
		current = int(time.time())
		expires = r.expire_in + current
		remind_in = r.get('remind_in', None)
		if remind_in:
			rtime = int(remind_in) + current
			if rtime < expires:
				expires = rtime
		return weibo.JsonDict(expires=expires, expires_in=expires, uid=r.get('uid', None))

	def set_uid(self, uid):
		self.uid = uid


TOKEN_FILE = 'token-record.log'
def load_tokens(filename=TOKEN_FILE):
	acc_tk_list = []
	try:
		filepath = os.path.join(os.path.dirname(__file__), filename)
		f = open(filepath)
		m = f.readline().strip()
		if m:
			acc_tk_list.append(m)
			print "===> Get the access_token from file token-record.log : ", acc_tk_list[0]
		else:
			print "===> roken-record.log is None!"
		f.close()
	except IOError:
		print "===> File token-record.log does not exist."
	return acc_tk_list


def dump_tokens(tk, filename=TOKEN_FILE):
	try:
		filepath = os.path.join(os.path.dirname(__file__), filename)
		f = open(filepath, 'a')
		f.write(tk)
		f.write('\n')
		f.close()
	except IOError:
		print "===> File token-record.log does not exist."
	print "===> The new access_token has been written to file token-record.log."

def get_client(appkey, appsecret, callback):
	at_list = load_tokens()
	client = myAPIClient(appkey, appsecret, callback)
	if at_list:
		access_token = at_list[-1]
		r = client.request_access_token_info(access_token)
		expires_in = r.expires_in
		print "===> The access_token's expires_in : %f" % expires_in
		if r.expires_in <= 0:
			return None
		client.set_uid(r.uid)
	else:
		auth_url = client.get_authorize_url()
		print "===> auth_url : " + auth_url 
		print "===> Note! The access_token is not available, you should be authorized again. Please open the url above in your browser, then you will get a returned url with the code field. Input the code in the follow step."
		code = raw_input("===> input the retured code : ")
		r = client.request_access_token(code)
		access_token = r.access_token
		expires_in = r.expires_in
		print "===> the new access_token is : ", access_token
		dump_tokens(access_token)
	client.set_access_token(access_token, expires_in)
	client.set_uid(r.uid)
	return client

