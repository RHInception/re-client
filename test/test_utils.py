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
import yaml
import os

import mock

from . import TestCase, unittest

from reclient import utils


class TestUtils(TestCase):

    def test_temp_blob(self):
        """
        Verify temp_blob works as expected.
        """

        for good in (
                unicode('{"test": "item"}'),  # Unicode
                '{"test": "item"}',  # str
                {"test": "item"}):  # dict
            tmp_file = utils.temp_blob(good, 'json')
            # Make sure the file exists
            assert os.path.exists(tmp_file.name)
            # Make sure the file loads as json
            assert json.load(open(tmp_file.name))

        # A playbook must be a dictionary, string or unicode
        for bad in (object(), 10):
            self.assertRaises(ValueError, utils.temp_blob, bad, 'json')

    def test_edit_playbook(self):
        """
        Verify calling the local editor works as expected.
        """
        # Call with temp file
        with mock.patch('reclient.utils.call') as utils.call:
            tmp_file = utils.temp_blob({'test': 'item'}, 'json')
            result = utils.edit_playbook(tmp_file, 'json')
            assert result == tmp_file
            utils.call.assert_called_once_with(['emacs', '-nw', tmp_file.name])

        # Call with temp file and vim
        with mock.patch('reclient.utils.call') as utils.call:
            os.environ['EDITOR'] = 'vim'
            tmp_file = utils.temp_blob({'test': 'item'}, 'json')
            result = utils.edit_playbook(tmp_file, 'json')
            assert result == tmp_file
            utils.call.assert_called_once_with(['vim', tmp_file.name])

        # Call with blob
        with mock.patch('reclient.utils.call') as utils.call:
            result = utils.edit_playbook({'test': 'item'}, 'json')
            utils.call.assert_callled_once_with(['emacs', '-nw', result.name])

        # Call with blob and vim
        with mock.patch('reclient.utils.call') as utils.call:
            os.environ['EDITOR'] = 'vim'
            result = utils.edit_playbook({'test': 'item'}, 'json')
            utils.call.assert_callled_once_with(['vim', result.name])

    def test_edit_playbook_editor_fallback(self):
        """
        Fall-back logic works as expected when selecting editor
        """
        del os.environ['EDITOR']

        m_u_c = mock.Mock(side_effect=OSError)
        with mock.patch('reclient.utils.call', m_u_c) as utils.call:
            os.environ['EDITOR'] = 'reclient_fake_editor_doesnt_exist'
            os.environ['PATH'] = ''
            result = utils.edit_playbook({'test': 'item'}, 'json')
            self.assertEqual(result, False)

    def test_less_file(self):
        """
        Make sure the system call to less works.
        """
        with mock.patch('reclient.utils.call') as utils.call:
            utils.less_file('/fake/file.txt')
            utils.call.assert_called_once_with([
                'less', '-X', '/fake/file.txt'])

    def test_serialize(self):
        """
        Make sure that serialization works as expected
        """
        data = {"test": "data"}
        yaml_ser = utils.serialize(data, 'yaml')
        json_ser = utils.serialize(data, 'json')

        assert yaml.safe_load(yaml_ser) == json.loads(json_ser)

    def test_deserialize(self):
        """
        Make sure that deserialization works as expected
        """
        data = {"test": "data"}
        yaml_dump = utils.deserialize(yaml.safe_dump(data), 'yaml')
        json_dump = utils.deserialize(json.dumps(data), 'json')
        assert yaml_dump == json_dump

    @mock.patch("reclient.utils.cooked_input")
    def test_user_prompt_yes_no_YES(self, cooked_input):
        """
        Test that the confirmation prompt works with an initial yes response
        """
        cooked_input.return_value = 'y'
        self.assertEqual(utils.user_prompt_yes_no(), True)
        cooked_input.return_value = 'Y'
        self.assertEqual(utils.user_prompt_yes_no(), True)

    @mock.patch("reclient.utils.cooked_input")
    def test_user_prompt_yes_no_NO(self, cooked_input):
        """
        Test that the confirmation prompt works with an initial no response
        """
        cooked_input.return_value = 'n'
        self.assertEqual(utils.user_prompt_yes_no(), False)
        cooked_input.return_value = 'N'
        self.assertEqual(utils.user_prompt_yes_no(), False)

    @mock.patch("reclient.utils.cooked_input")
    def test_user_prompt_yes_no_Invalid_then_Yes(self, cooked_input):
        """
        Test that the confirmation prompt works for Yes after an initial invalid response
        """
        returns = ["yesyesyes", "Y"]
        def side_effect(*args, **kwargs):
            return returns.pop(0)

        cooked_input.side_effect = side_effect
        self.assertEqual(utils.user_prompt_yes_no(), True)
        self.assertEqual(cooked_input.call_count, 2)

    @mock.patch("reclient.utils.cooked_input")
    def test_user_prompt_yes_no_Invalid_then_No(self, cooked_input):
        """
        Test that the confirmation prompt works for No after an initial invalid response
        """
        returns = ["nonono", "N"]
        def side_effect(*args, **kwargs):
            return returns.pop(0)

        cooked_input.side_effect = side_effect
        self.assertEqual(utils.user_prompt_yes_no(), False)
        self.assertEqual(cooked_input.call_count, 2)
