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


from reclient.connectors import Connectors
import reclient.utils
import json

"""
Handles basic HTTP authentication to the rerest endpoint.
"""


class ReClient(object):
    def __init__(self, baseurl, version='v0'):
        self.v = version
        self.baseurl = baseurl
        self._config()

    def _config(self):
        """Get the endpoint configuration"""
        username = "foo"
        password = "bar"
        self.endpoint = "%s/api/%s/" % (self.baseurl, self.v)
        self.connector = Connectors({
            "name": "foo",
            "password": "bar",
            "baseurl": self.endpoint
        })

    def get_all_playbooks_ever(self):
        """Get ALL THE PLAYBOOKS"""
        suffix = "playbooks/"
        result = self.connector.get(suffix)['items']
        view_file = reclient.utils.temp_json_blob(result)
        reclient.utils.less_file(view_file.name)

    def get_all_playbooks(self, project):
        """
        Get all playbooks that match `project`
        """
        suffix = "%s/playbook/" % project
        result = self.connector.get(suffix)
        print "[%s] - %s" % (result.status_code,
                             result.json())

    def _get_playbook(self, project, pb_id):
        """project - name of the project to search for playbook with id 'pb_id'

Return a two-tuple of the serialized datastructure, as well as a
reference to tthe tempfile.NamedTemporaryFile object it has been
written out to.
        """
        suffix = "%s/playbook/%s/" % (project, pb_id)
        # Make REST call to fetch the playbook
        result = self.connector.get(suffix)
        # We get a hash back, part of it is the status code. Lets just
        # get straight to the playbook in 'item'
        pb_blob = result.json()['item']
        # Write it out to a temporary file
        pb_fp = reclient.utils.temp_json_blob(pb_blob)
        return (result.json()['item'], pb_fp)

    def _send_playbook(self, project, pb_id, pb_fp):
        suffix = "%s/playbook/%s/" % (project, pb_id)
        with open(pb_fp.name, 'r') as pb_open:
            return self.connector.post(suffix, data=pb_open)

    def view_file(self, project, pb_id):
        (pb, path) = self._get_playbook(project, pb_id)
        reclient.utils.less_file(path.name)

    def edit_playbook(self, project, pb_id):
        (pb, path) = self._get_playbook(project, pb_id)
        pb_fp = reclient.utils.edit_playbook(path)
        while True:
            send_back = raw_input("Upload [N/y]? ")
            if send_back.lower() == 'y':
                try:
                    self._send_playbook(project, pb_id, pb_fp)
                except IOError, ioe:
                    raise ioe
                finally:
                    break
            elif send_back.lower() == 'n':
                print "OK. Your loss."
                break
