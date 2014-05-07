# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64
import requests
import logging
out = logging.getLogger('reclient')


class Connectors(object):
    def __init__(self, connect_params, reclient_version='0.0.0'):
        """
        connect_params.keys() = ['name', 'password', 'baseurl']
        """
        self.baseurl = connect_params['baseurl']
        self.auth = (connect_params['name'], connect_params['password'])
        auth_header = base64.encodestring('%s:%s' % self.auth)[:-1]
        self.headers = {
            "content-type": "application/json",
            "Authorization": "Basic %s" % auth_header,
            "User-Agent": "reclient/%s" % reclient_version
        }

    def delete(self, url=""):
        url = self.baseurl + url
        out.debug("DELETE request send to: %s" % url)
        response = requests.delete(url, headers=self.headers, verify=False)
        out.debug("Response:")
        try:
            out.debug(response.json())
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response

    def get(self, url=""):
        url = self.baseurl + url
        out.debug("GET request send to: %s" % url)
        response = requests.get(url, headers=self.headers, verify=False)
        out.debug("Response:")
        try:
            out.debug(response.json())
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response

    def post(self, url="", data={}):
        url = self.baseurl + url
        out.debug("POST request send to: %s" % url)
        out.debug("Data: %s" % str(data))
        response = requests.post(url, data, headers=self.headers, verify=False)
        out.debug("Response:")
        try:
            out.debug(response.json())
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response

    def put(self, url="", data={}):
        url = self.baseurl + url
        out.debug("PUT request send to: %s" % url)
        out.debug("Data: %s" % str(data))
        response = requests.put(url, data, headers=self.headers, verify=False)
        out.debug("Response:")
        try:
            out.debug(response.json())
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response
