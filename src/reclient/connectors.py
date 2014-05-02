import base64
import requests

class Connectors(object):
    def __init__(self, connect_params):
        """
        connect_params.keys() = ['name', 'password', 'baseurl']
        """
        self.baseurl = connect_params['baseurl']
        self.auth = (connect_params['name'], connect_params['password'])
        auth_header = base64.encodestring('%s:%s' % self.auth)[:-1]
        self.headers = {
            'content-type': 'application/json',
            "Authorization": "Basic %s" % auth_header
        }
        # print self.baseurl
        # print self.headers
        # print self.auth

    def delete(self, url=""):
        url = self.baseurl + url
        return requests.delete(url, headers=self.headers, verify=False)

    def get(self, url=""):
        url = self.baseurl + url
        return requests.get(url, headers=self.headers, verify=False)

    def post(self, url="", data={}):
        url = self.baseurl + url
        return requests.post(url, data, headers=self.headers, verify=False)

    def put(self, url="", data={}):
        url = self.baseurl + url
        return requests.put(url, data, headers=self.headers, verify=False)
