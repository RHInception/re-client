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

from contextlib import nested
from requests_kerberos import HTTPKerberosAuth
from . import TestCase, unittest

from reclient import connectors


HTTP_AUTH = ('name', 'password')
PARAMS = {
    'baseurl': 'http://127.0.0.1/',
    'auth': HTTP_AUTH,
}

KERB_AUTH = HTTPKerberosAuth()
KERB_PARAMS = {
    'baseurl': 'https://127.0.0.1/',
    'auth': KERB_AUTH,
}

class TestConnectors(TestCase):

    def setUp(self):
        """
        Set up for each test.
        """
        TestCase.setUp(self)
        self.connector = connectors.Connectors(PARAMS)
        self.kerb_connector = connectors.Connectors(KERB_PARAMS)

    def test_connector_creation(self):
        """
        Verify creating the connector does what we expect.
        """
        assert self.connector.baseurl == PARAMS['baseurl']
        assert self.connector.auth == ('name', 'password')
        assert self.connector.headers["content-type"] == "application/json"

        assert self.kerb_connector.baseurl == KERB_PARAMS['baseurl']
        assert self.kerb_connector.auth == KERB_AUTH
        assert self.kerb_connector.headers["content-type"] == "application/json"

    def test_delete(self):
        """
        Make sure the connector uses the right delete call.
        """
        with nested(
                    mock.patch('reclient.connectors.requests.delete'),
                    mock.patch('getpass.getpass')
                ) as (delete, getpass):
            getpass.return_value = 'password'

            self.connector.delete('/test')
            delete.assert_called_once_with(
                self.connector.baseurl + '/test',
                auth=HTTP_AUTH,
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

            delete.reset_mock()
            self.kerb_connector.delete('/test')
            delete.assert_called_once_with(
                self.kerb_connector.baseurl + '/test',
                auth=KERB_AUTH,
                headers=self.kerb_connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!



    def test_get(self):
        """
        Make sure the connector uses the right get call.
        """
        with nested(
                    mock.patch('reclient.connectors.requests.get'),
                    mock.patch('getpass.getpass')
                ) as (get, getpass):
            self.connector.get('/test')
            get.assert_called_once_with(
                self.connector.baseurl + '/test',
                auth=HTTP_AUTH,
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

            get.reset_mock()
            self.kerb_connector.get('/test')
            get.assert_called_once_with(
                self.kerb_connector.baseurl + '/test',
                auth=KERB_AUTH,
                headers=self.kerb_connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

    def test_post(self):
        """
        Make sure the connector uses the right post call.
        """
        with nested(
                    mock.patch('reclient.connectors.requests.post'),
                    mock.patch('getpass.getpass')
                ) as (post, getpass):
            data = '{"test": "item"}'
            self.connector.post('/test', data)
            post.assert_called_once_with(
                self.connector.baseurl + '/test',
                data,
                auth=HTTP_AUTH,
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

            post.reset_mock()
            self.kerb_connector.post('/test', data)
            post.assert_called_once_with(
                self.kerb_connector.baseurl + '/test',
                data,
                auth=KERB_AUTH,
                headers=self.kerb_connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!


    def test_put(self):
        """
        Make sure the connector uses the right put call.
        """
        with nested(
                    mock.patch('reclient.connectors.requests.put'),
                    mock.patch('getpass.getpass')
                ) as (put, getpass):

            data = '{"test": "item"}'
            self.connector.put('/test', data)
            put.assert_called_once_with(
                self.connector.baseurl + '/test',
                data,
                auth=HTTP_AUTH,
                headers=self.connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!

            put.reset_mock()
            self.kerb_connector.put('/test', data)
            put.assert_called_once_with(
                self.kerb_connector.baseurl + '/test',
                data,
                auth=KERB_AUTH,
                headers=self.kerb_connector.headers,
                verify=False)  # TODO: Don't skip verification!!!!!!
