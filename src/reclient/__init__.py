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

"""Handles basic HTTP authentication and calls to the rerest
endpoint."""


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

    def _get_playbook(self, project, pb_id=None):
        """project - name of the project to search for playbook with id
'pb_id'. Omit pb_id and you get all playbooks for 'project'.

Return a two-tuple of the serialized datastructure, as well as a
reference to the tempfile.NamedTemporaryFile object it has been
written out to.
        """
        if pb_id is None:
            # Get all playbooks for 'project'
            suffix = "%s/playbook/" % project
        else:
            # Get a single playbook
            suffix = "%s/playbook/%s/" % (project, pb_id)

        result = self.connector.get(suffix)
        if result.status_code == 200:
            pb_blob = result.json()
            # Write it out to a temporary file
            pb_fp = reclient.utils.temp_json_blob(pb_blob)
            return (pb_blob, pb_fp)
        else:
            raise ReClientGETError(result)

    def _send_playbook(self, project, pb_fp, pb_id=None):
        """Send a playbook to the REST endpoint. Note the ordering of the
args/kwargs as they're ordered differently than most other methods.

`pb_fp` - File pointer to a playbook file
`pb_id` - OPTIONAL - if 'None' then this is interpreted as a NEW
playbook. If not 'None' then this is interpreted as an update to an
existing playbook.
        """
        if pb_id:
            # UPDATE
            print "Updating an existing playbook"
            suffix = "%s/playbook/%s/" % (project, pb_id)
            with open(pb_fp.name, 'r') as pb_open:
                result = self.connector.post(suffix, data=pb_open)
        else:
            # NET-NEW
            print "Sending a new playbook"
            suffix = "%s/playbook/" % project
            with open(pb_fp.name, 'r') as pb_open:
                result = self.connector.put(suffix, data=pb_open)

        code = result.status_code
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        if code == 200:
            # 200 = "OK" - Updated a playbook
            print "[%d] Updated playbook" % code
        elif code == 201:
            # 201 = "Created";
            print "[%d] Created new playbook" % code
        else:
            print "[%d] Unexpected response from rerest endpoint" % (
                code)
            raise ReClientSendError(result)

        print result.text
        return result

    def get_all_playbooks_ever(self):
        """Get ALL THE PLAYBOOKS"""
        suffix = "playbooks/"
        result = self.connector.get(suffix)
        view_file = reclient.utils.temp_json_blob(result.json())
        reclient.utils.less_file(view_file.name)

    def get_all_playbooks(self, project):
        """
        Get all playbooks that match `project`
        """
        try:
            (path, pb_fp) = self._get_playbook(project)
        except REClientGETError, e:
            print "Error while attempting to get playbooks for project: %s" % (
                project)
            raise e
        reclient.utils.less_file(pb_fp.name)

    def view_file(self, project, pb_id):
        """
        Open playbook with id `pd_id` in `project` with the /bin/less command
        """
        try:
            (pb, path) = self._get_playbook(project, pb_id)
        except ReClientGETError, e:
            print "Error while attempting to find '%s' for project '%s'" % (
                pb_id, project)
            print "Are you sure it exists?"
        else:
            reclient.utils.less_file(path.name)

    def edit_playbook(self, project, pb_id):
        (pb, path) = self._get_playbook(project, pb_id)
        pb_fp = reclient.utils.edit_playbook(path)
        while True:
            send_back = raw_input("Upload [N/y]? ")
            if send_back.lower() == 'y':
                try:
                    result = self._send_playbook(project, pb_fp, pb_id)
                except IOError, ioe:
                    raise ioe
                except ReClientSendError, rcse:
                    print "Error while sending updated playbook: %s" % (
                        str(rcse))
                finally:
                    break
            elif send_back.lower() == 'n':
                print "Not sending back. Playbook will be saved in %s" % (
                    pb_fp.name)
                print "until this program is closed."
                break

    def delete_playbook(self, project, pb_id):
        suffix = "%s/playbook/%s/" % (project, pb_id)
        result = self.connector.delete(suffix)
        return result

    def new_playbook(self, project):
        suffix = "%s/playbook/" % project
        pb = {
            "project": project,
            "ownership": {
                "id": None,
                "contact": None
            },
            "steps": []
        }
        pb_fp = reclient.utils.temp_json_blob(pb)
        reclient.utils.edit_playbook(pb_fp)
        self._send_playbook(project, pb_fp)

class ReClientError(Exception):
    pass

class ReClientGETError(ReClientError):
    pass

class ReClientSendError(ReClientError):
    pass
