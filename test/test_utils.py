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

from . import TestCase, unittest

from reclient import utils


class TestUtils(TestCase):

    def test_temp_json_blob(self):
        """
        Verify temp_json_blog works as expected.
        """

        for good in (
                unicode('{"test": "item"}'),  # Unicode
                '{"test": "item"}',  # str
                {"test": "item"}):  # dict
            tmp_file = utils.temp_json_blob(good)
            # Make sure the file exists
            assert os.path.exists(tmp_file.name)
            # Make sure the file loads as json
            assert json.load(open(tmp_file.name))

        # A playbook must be a dictionary, string or unicode
        for bad in (object(), 10):
            self.assertRaises(ValueError, utils.temp_json_blob, bad)

    def test_edit_playbook(self):
        """
        Verify calling the local editor works as expected.
        """
        # Call with temp file
        with mock.patch('reclient.utils.call') as utils.call:
            tmp_file = utils.temp_json_blob({'test': 'item'})
            result = utils.edit_playbook(tmp_file)
            assert result == tmp_file
            utils.call.assert_called_once_with(['emacs', '-nw', tmp_file.name])

        # Call with temp file and vim
        with mock.patch('reclient.utils.call') as utils.call:
            os.environ['EDITOR'] = 'vim'
            tmp_file = utils.temp_json_blob({'test': 'item'})
            result = utils.edit_playbook(tmp_file)
            assert result == tmp_file
            utils.call.assert_called_once_with(['vim', tmp_file.name])

        # Call with blob
        with mock.patch('reclient.utils.call') as utils.call:
            result = utils.edit_playbook({'test': 'item'})
            utils.call.assert_callled_once_with(['emacs', '-nw', result.name])

        # Call with blob and vim
        with mock.patch('reclient.utils.call') as utils.call:
            os.environ['EDITOR'] = 'vim'
            result = utils.edit_playbook({'test': 'item'})
            utils.call.assert_callled_once_with(['vim', result.name])

    def test_less_file(self):
        """
        Make sure the system call to less works.
        """
        with mock.patch('reclient.utils.call') as utils.call:
            utils.less_file('/fake/file.txt')
            utils.call.assert_called_once_with([
                'less', '-X', '/fake/file.txt'])
