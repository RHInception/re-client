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
    def __init__(self, connect_params, format, reclient_version='0.0.5'):
        """
        connect_params.keys() = ['auth', 'baseurl']
        """
        self.baseurl = connect_params['baseurl']
        self.auth = connect_params['auth']
        self.headers = {
            "User-Agent": "reclient/%s" % reclient_version,
        }
        if format == 'json':
            self.headers["content-type"] = "application/json"
        else:
            self.headers["content-type"] = "text/yaml"
        #: The GET string to add at the end to specify format
        self._format_get_str = "?format=%s" % format

    def delete(self, url=""):
        """
        Deletes a playbook.
        """
        url = self.baseurl + url + self._format_get_str
        out.debug("DELETE request send to: %s" % url)
        response = requests.delete(
            url, headers=self.headers, verify=False, auth=self.auth)
        out.debug("Response:")
        try:
            out.debug(response.content)
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response

    def get(self, url=""):
        """
        Gets a playbook.
        """
        url = self.baseurl + url + self._format_get_str
        out.debug("GET request send to: %s" % url)
        response = requests.get(
            url, headers=self.headers, verify=False, auth=self.auth)
        out.debug("Response:")
        try:
            out.debug(response.content)
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response

    def post(self, url="", data={}):
        """
        Modifies a playbook.
        """
        url = self.baseurl + url + self._format_get_str
        out.debug("POST request send to: %s" % url)
        out.debug("Data: %s" % str(data))
        response = requests.post(
            url, data, headers=self.headers, verify=False, auth=self.auth)
        out.debug("Response:")
        try:
            out.debug(response.content)
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response

    def put(self, url="", data={}):
        """
        Creates a playbook/
        """
        url = self.baseurl + url + self._format_get_str
        out.debug("PUT request send to: %s" % url)
        out.debug("Data: %s" % str(data))
        response = requests.put(
            url, data, headers=self.headers, verify=False, auth=self.auth)
        out.debug("Response:")
        try:
            out.debug(response.content)
        except Exception:
            # Might not be loadable if it's a weird error
            out.debug(str(response.text))
        return response
