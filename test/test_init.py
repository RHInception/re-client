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
import pwd
import mock

import reclient

from contextlib import nested
from . import TestCase, unittest

BASEURL = 'http://127.0.0.1/'
VERSION = 'v0'
PROJECT = 'test'
ID = '12345'
reclient_config = {
    'baseurl': BASEURL,
    'username': pwd.getpwuid(os.getuid())[0]
}

AUTH = (pwd.getpwuid(os.getuid())[0], 'password')



class TestInit(TestCase):

    def setUp(self):
        """
        Set up for tests.
        """
        reclient.reclient_config = reclient_config
        with mock.patch('getpass.getpass') as getpass:
            getpass.return_value = 'password'
            self.reclient = reclient.ReClient(format='yaml')

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
        with mock.patch('getpass.getpass') as getpass:
            getpass.return_value = 'password'
            self.reclient._config()
            assert self.reclient.endpoint == "%s/api/%s/" % (BASEURL, VERSION)
            assert self.reclient.connector.baseurl == self.reclient.endpoint
            print pwd.getpwuid(os.getuid())[0]
            assert self.reclient.connector.auth == AUTH

    def test__get_playbook(self):
        """
        Verify _get_playbook follows the correct pattern to get a playbook.
        """
        # Without an id
        with mock.patch('reclient.connectors.requests.get') as get:
            response = mock.MagicMock(status_code=200)
            response.content = '{items: item}\n'
            get.return_value = response
            with mock.patch('reclient.utils.temp_blob') as jb:
                results = self.reclient._get_playbook(PROJECT)
                get.assert_called_once_with(
                    self.reclient.endpoint + PROJECT + '/playbook/?format=yaml',
                    auth=AUTH,
                    verify=False,
                    headers=self.reclient.connector.headers)
                assert results[0] == "item"
                assert results[1] == jb()

        # With an id
        with mock.patch('reclient.connectors.requests.get') as get:
            response = mock.MagicMock(status_code=200)
            response.content = '{item: item}\n'
            get.return_value = response
            with mock.patch('reclient.utils.temp_blob') as jb:
                results = self.reclient._get_playbook(PROJECT, ID)
                get.assert_called_once_with(
                    self.reclient.endpoint + PROJECT + '/playbook/' + ID + "/?format=yaml",
                    auth=AUTH,
                    verify=False,
                    headers=self.reclient.connector.headers)
                print results
                assert results[0] == "item"
                assert results[1] == jb()

    def test__send_playbook(self):
        """
        Verify _send_playbook follows the correct pattern to send a playbook.
        """
        # Without an id
        with mock.patch('reclient.connectors.requests.put') as put:
            response = mock.MagicMock(status_code=201)
            response.content = '{items: item}\n'
            put.return_value = response

            fp = mock.MagicMock('fp')
            fp.name = 'test/example.json'

            results = self.reclient._send_playbook(PROJECT, fp)

            put.assert_called_once_with(
                self.reclient.endpoint + PROJECT + '/playbook/?format=yaml',
                mock.ANY,  # Using ANY as we can't anticipate the fileid
                auth=AUTH,
                verify=False,
                headers=self.reclient.connector.headers)
            assert results == put()

        # With an id
        with mock.patch('reclient.connectors.requests.post') as post:
            response = mock.MagicMock(status_code=200)
            response.content = '{item: item}\n'
            post.return_value = response

            fp = mock.MagicMock('fp')
            fp.name = 'test/example.json'

            results = self.reclient._send_playbook(PROJECT, fp, ID)

            post.assert_called_once_with(
                self.reclient.endpoint + PROJECT + '/playbook/' + ID + '/?format=yaml',
                mock.ANY,  # Using ANY as we can't anticipate the fileid
                auth=AUTH,
                verify=False,
                headers=self.reclient.connector.headers)
            assert results == post()

        # With unexpected response
        with mock.patch('reclient.connectors.requests.post') as post:
            response = mock.MagicMock(status_code=302)
            response.content = '{items: item}\n'
            post.return_value = response

            fp = mock.MagicMock('fp')
            fp.name = 'test/example.json'

            # We should get a raise of ReClientSendError
            self.assertRaises(
                reclient.ReClientSendError,
                self.reclient._send_playbook,
                PROJECT, fp, ID)

    def test_get_all_playbooks_ever(self):
        """
        get_all_playbooks_ever should do just that."
        """
        with nested(
                mock.patch('reclient.connectors.requests.get'),
                mock.patch('reclient.utils.less_file'),
                mock.patch('reclient.utils.temp_blob')) as (get, less_file, jb):
            response = mock.MagicMock(status_code=200)
            response.content = '{status: ok}\n'
            get.return_value = response

            # There should be nothing returned
            all_pb_call_result = self.reclient.get_all_playbooks_ever()
            print all_pb_call_result
            assert all_pb_call_result is None
            # Verify the remote call
            get.assert_called_once_with(
                self.reclient.endpoint + 'playbooks/?format=yaml',
                headers=self.reclient.connector.headers,
                auth=AUTH,
                verify=False)
            # And the following support calls
            assert jb.call_count == 1
            assert less_file.call_count == 1

    def test_view_file(self):
        """
        Verify vewing a file does what it should.
        """
        # Exists
        with mock.patch('reclient.ReClient._get_playbook') as get_pb:
            m_path = mock.MagicMock('path')
            m_path.name = 'test/example.json'
            get_pb.return_value = (mock.MagicMock('pb'), m_path)

            with mock.patch('reclient.utils.less_file') as less_file:
                self.reclient.view_file(PROJECT, ID)
                assert less_file.call_count == 1

        # Does not exists
        with mock.patch('reclient.ReClient._get_playbook') as get_pb:
            get_pb.side_effect = reclient.ReClientGETError('Does not exist')

            with mock.patch('reclient.utils.less_file') as less_file:
                assert less_file.call_count == 0

    def test_edit_playbook(self):
        """
        Users should be able to edit a playbook.
        """
        # Without sending back
        with nested(
                mock.patch('reclient.ReClient._get_playbook'),
                mock.patch('reclient.utils.deserialize')) as (get_pb, ds):
            m_path = mock.MagicMock('path')
            m_path.name = 'test/example.json'
            get_pb.return_value = (mock.MagicMock('pb'), m_path)
            with mock.patch('reclient.utils.edit_playbook') as edit_pb:
                # Nothing is returned
                assert self.reclient.edit_playbook(
                    PROJECT, ID, noop=True) is None

        # With sending back
        with nested(
                mock.patch('reclient.ReClient._get_playbook'),
                mock.patch('reclient.utils.deserialize')) as (get_pb, ds):
            m_path = mock.MagicMock('path')
            m_path.name = 'test/example.json'
            get_pb.return_value = (mock.MagicMock('pb'), m_path)
            with mock.patch('reclient.utils.edit_playbook') as edit_pb:
                with mock.patch('reclient.ReClient._send_playbook') as send_pb:
                    result = self.reclient.edit_playbook(
                        PROJECT, ID, noop=False)
                    # The result should be from the call of _send_playbook
                    assert result == send_pb()

    def test_delete_playbook(self):
        """
        Users should be able to delete a playbook.
        """
        with mock.patch('reclient.connectors.requests.delete') as delete:
            response = mock.MagicMock(status_code=410)
            delete.return_value = response
            result = self.reclient.delete_playbook(PROJECT, ID)

            delete.assert_called_once_with(
                self.reclient.endpoint + PROJECT + '/playbook/' + ID + "/?format=yaml",
                verify=False,
                auth=AUTH,
                headers=self.reclient.connector.headers)
            # The result is simply the return data from delete
            assert result == delete()

    def test_new_playbook(self):
        """
        Users should be able to create a new playbook.
        """
        with nested(
                mock.patch('reclient.utils.edit_playbook'),
                mock.patch('reclient.ReClient._send_playbook'),
                mock.patch('reclient.utils.temp_blob')) as (edit_pb, send_pb, jb):
            self.reclient.new_playbook(PROJECT)
            # These items must be called to make a new playbook
            assert jb.call_count == 1
            assert edit_pb.call_count == 1
            assert send_pb.call_count == 1

    def test_download_playbook(self):
        """
        We can save playbooks locally
        """
        with nested(
                mock.patch('reclient.ReClient._get_playbook'),
                mock.patch('reclient.utils.save_playbook')) as (get_pb, save_pb):
            save_path = '/tmp/pb.json'
            fake_pb = {'test': 'playbook'}
            fake_tmp_file = mock.Mock(spec=file)
            get_pb.return_value = (fake_pb, fake_tmp_file)

            self.reclient.download_playbook(save_path, PROJECT, ID)
            save_pb.assert_called_once_with(fake_pb, save_path)

    def test_upload_playbook(self):
        """
        We can upload saved playbooks
        """
        with nested(
                mock.patch('reclient.ReClient._send_playbook'),
                mock.patch('reclient.open', create=True),
                mock.patch('reclient.colorize')) as (send_pb, mock_open, color):
            source_path = '/tmp/fake_pb.yaml'
            send_pb.return_value.content = '{id: 1234567890}'

            self.reclient.upload_playbook(source_path, PROJECT)

            # colorize is called twice, once to highlight the pb id,
            # and once to print the success message
            assert color.call_count == 2

            assert send_pb.called_once_with(PROJECT, mock_open.__enter__)

    def test_start_deployment(self):
        """
        We can start a new deployment correctly
        """

        with mock.patch('reclient.connectors.requests.put') as put:
            response = mock.MagicMock(status_code=201)
            response.content = '{"status": "created"}'
            put.return_value = response
            result = self.reclient.start_deployment(PROJECT, ID)
            put.assert_called_once_with(
                self.reclient.endpoint + PROJECT + '/playbook/' + ID + "/deployment/?format=yaml",
                {},
                auth=AUTH,
                verify=False,
                headers=self.reclient.connector.headers)
            # The result is simply the return data from put
            assert result == put()

        with mock.patch('reclient.connectors.requests.put') as put:
            response = mock.MagicMock(status_code=403)
            response.content = '{"status": "error", "message": "Faked a bad deployment"}'

            put.return_value = response

            result = self.reclient.start_deployment(PROJECT, ID)
            put.assert_called_once_with(
                self.reclient.endpoint + PROJECT + '/playbook/' + ID + "/deployment/?format=yaml",
                {},
                auth=AUTH,
                verify=False,
                headers=self.reclient.connector.headers)
            print result
            assert result == False
