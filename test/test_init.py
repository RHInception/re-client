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

import json
import os

import mock

import reclient

from . import TestCase, unittest

BASEURL = 'http://127.0.0.1/'
VERSION = 'v0'


class TestInit(TestCase):

    def setUp(self):
        """
        Set up for tests.
        """
        self.reclient = reclient.ReClient(BASEURL, VERSION)

    def test_reclient_init(self):
        """
        Verify the object is creatd how we expect.
        """
        assert self.reclient.baseurl == BASEURL
        assert self.reclient.v == VERSION
        assert self.reclient.endpoint == "%s/api/%s/" % (BASEURL, VERSION)

    def test__config(self):
        """
        Make sure config sets the right items when called.
        """
        self.reclient._config()
        assert self.reclient.endpoint == "%s/api/%s/" % (BASEURL, VERSION)
        assert self.reclient.connector.baseurl == self.reclient.endpoint
        assert self.reclient.connector.auth == ('foo', 'bar')  # FIXME

    def test__get_playbook(self):
        """
        Verify _get_playbook follows the correct pattern to get a playbook.
        """
        project = 'test'
        id = '12345'

        # Without an id
        with mock.patch('reclient.connectors.requests.get') as get:
            response = mock.MagicMock(status_code=200)
            response.json.return_value = '{"test": "item"}'
            get.return_value = response
            with mock.patch('reclient.utils.temp_json_blob') as jb:
                results = self.reclient._get_playbook(project)
                get.assert_called_once_with(
                    self.reclient.endpoint + project + '/playbook/',
                    verify=False,
                    headers=self.reclient.connector.headers)
                print results
                assert results[0] == '{"test": "item"}'
                assert results[1] == jb()

        # With an id
        with mock.patch('reclient.connectors.requests.get') as get:
            response = mock.MagicMock(status_code=200)
            response.json.return_value = '{"test": "item"}'
            get.return_value = response
            with mock.patch('reclient.utils.temp_json_blob') as jb:
                results = self.reclient._get_playbook(project, id)
                get.assert_called_once_with(
                    self.reclient.endpoint + project + '/playbook/' + id + "/",
                    verify=False,
                    headers=self.reclient.connector.headers)
                print results
                assert results[0] == '{"test": "item"}'
                assert results[1] == jb()

    def test_get_all_playbooks_ever(self):
        """
        get_all_playbooks_ever should do just that."
        """
        with mock.patch('reclient.connectors.requests.get') as get:
            with mock.patch('reclient.utils.less_file') as less_file:
                with mock.patch('reclient.utils.temp_json_blob') as jb:
                    # There should be nothing returned
                    assert self.reclient.get_all_playbooks_ever() is None
                    # Verify the remote call
                    get.assert_called_once_with(
                        self.reclient.endpoint + 'playbooks/',
                        headers=self.reclient.connector.headers,
                        verify=False)
                    # And the following support calls
                    assert jb.call_count == 1
                    assert less_file.call_count == 1
