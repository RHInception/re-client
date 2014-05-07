# Copyright (C) 2014 SEE AUTHORS FILE
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
"""
Unittests.
"""

import base64
import json
import os

import mock

from . import TestCase, unittest

from reclient import connectors

PARAMS = {
    'baseurl': 'http://127.0.0.1/',
    'name': 'name',
    'password': 'password',
}


class TestConnectors(TestCase):

    def setUp(self):
        """
        Set up for each test.
        """
        TestCase.setUp(self)
        self.connector = connectors.Connectors(PARAMS)

    def test_connector_creation(self):
        """
        Verify creating the connector does what we expect.
        """
        assert self.connector.baseurl == PARAMS['baseurl']
        assert self.connector.auth == (PARAMS['name'], PARAMS['password'])
        assert self.connector.headers["content-type"] == "application/json"
        basic_str = '%s:%s' % (PARAMS['name'], PARAMS['password'])
        assert base64.decodestring(
            self.connector.headers["Authorization"][6:]) == basic_str

    def test_delete(self):
        """
        Make sure the connector uses the right delete call.
        """
        with mock.patch('reclient.connectors.requests.delete') as delete:
            self.connector.delete('/test')
            delete.assert_called_once_with(
                self.connector.baseurl + '/test',
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

    def test_get(self):
        """
        Make sure the connector uses the right get call.
        """
        with mock.patch('reclient.connectors.requests.get') as get:
            self.connector.get('/test')
            get.assert_called_once_with(
                self.connector.baseurl + '/test',
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

    def test_post(self):
        """
        Make sure the connector uses the right post call.
        """
        with mock.patch('reclient.connectors.requests.post') as post:
            data = '{"test": "item"}'
            self.connector.post('/test', data)
            post.assert_called_once_with(
                self.connector.baseurl + '/test',
                data,
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

    def test_put(self):
        """
        Make sure the connector uses the right put call.
        """
        with mock.patch('reclient.connectors.requests.put') as put:
            data = '{"test": "item"}'
            self.connector.put('/test', data)
            put.assert_called_once_with(
                self.connector.baseurl + '/test',
                data,
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!
