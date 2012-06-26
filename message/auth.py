# -*- encoding: utf-8
import re
import urllib
import urllib2

from django.core.cache import cache

CLIENT_LOGIN_URL = 'https://www.google.com/accounts/ClientLogin'

class TokensManager(object):

    KEY_CACHE_CLIENTLOGIN_TOKEN = 'c2dm_clientlogin_token'
    KEY_CACHE_TIMEOUT = 86400 # one day

    def __init__(self, user, password, account_type, app_name):
        self.user = user
        self.password = password
        self.account_type = account_type
        self.app_name = app_name
        self.token = cache.get(self.KEY_CACHE_CLIENTLOGIN_TOKEN, '')
        if not self.token:
            self.renew()

    def renew(self):
        values = {
            'accountType': self.account_type,
            'Email': self.user,
            'Passwd': self.password,
            'service': 'ac2dm',
            'source': self.app_name,
        }
        params = urllib.urlencode(values)
        request = urllib2.Request(CLIENT_LOGIN_URL, params)
        self.response = urllib2.urlopen(request)
        self.response_data = self.decode_response(self.response.read())
        self.token = self.response_data['Auth']
        if self.token:
            cache.set(self.KEY_CACHE_CLIENTLOGIN_TOKEN, self.token,
                      self.KEY_CACHE_TIMEOUT)

    def decode_response(self, data):
        return dict(re.findall('(.+)=(.+)', data, re.M))

    def __unicode__(self):
        return self.token

    def __str__(self):
        return self.token
