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
from reclient.colorize import colorize
import reclient.utils
import logging

"""Handles basic HTTP authentication and calls to the rerest
endpoint."""

out = logging.getLogger('recore')
reclient_config = {}


class ReClient(object):
    def __init__(self, version='v0', debug=1):
        self.v = version
        self.debug = debug
        self.baseurl = reclient_config['baseurl']
        self._config()

    def _config(self):
        """Get the endpoint configuration"""
        self.endpoint = "%s/api/%s/" % (self.baseurl, self.v)
        self.connector = Connectors({
            "name": reclient_config['username'],
            "password": "foobar",
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
            key = "items"
        else:
            # Get a single playbook
            suffix = "%s/playbook/%s/" % (project, pb_id)
            key = "item"

        result = self.connector.get(suffix)
        if result.status_code == 200:
            pb_blob = result.json()[key]

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
        try:
            response_msg = result.json()
            if response_msg['status'] == 'error':
                print colorize(
                    "Error while fetching all playbooks", color="red",
                    background="lightgray")
                print colorize(
                    "%s - %s" % (str(result), response_msg), color="red",
                    background="lightgray")
                raise ReClientGETError(result)
        except Exception:
            return False
        else:
            view_file = reclient.utils.temp_json_blob(result.json())
            reclient.utils.less_file(view_file.name)

    def get_all_playbooks(self, project):
        """
        Get all playbooks that match `project`
        """
        try:
            (path, pb_fp) = self._get_playbook(project)
        except ReClientGETError, e:
            response_msg = e.args[0].json()
            print colorize("Error while fetching playbooks for %s:" % project,
                           color="red",
                           background="lightgray")
            print colorize(
                "%s - %s" % (
                    str(e),
                    response_msg['message']),
                color="red", background="lightgray")
        else:
            reclient.utils.less_file(pb_fp.name)

    def view_file(self, project, pb_id):
        """
        Open playbook with id `pd_id` in `project` with the /bin/less command
        """
        try:
            (pb, path) = self._get_playbook(project, pb_id)
        except ReClientGETError:
            print colorize((
                "Error while attempting to find '%s' for project '%s'\n"
                "Are you sure it exists?") % (
                pb_id, project),
                color="red",
                background="lightgray")
            print ""
        else:
            reclient.utils.less_file(path.name)

    def edit_playbook(self, project, pb_id, noop=None):
        try:
            (pb, path) = self._get_playbook(project, pb_id)
        except ReClientGETError, rcge:
            response_msg = rcge.args[0].json()
            print colorize("Error while fetching playbooks for %s:" % project,
                           color="red",
                           background="lightgray")
            print colorize(
                "%s - %s" % (
                    str(rcge),
                    response_msg['message']),
                color="red", background="lightgray")
            return False

        pb_fp = reclient.utils.edit_playbook(path)
        while True:
            if noop:
                send_back = 'n'
            elif not noop:
                send_back = 'y'
            else:
                send_back = input("Upload [Y/n]? ")

            if send_back.lower() == 'y' or send_back.strip() == '':
                try:
                    result = self._send_playbook(project, pb_fp, pb_id)
                except IOError, ioe:
                    raise ioe
                except ReClientSendError, rcse:
                    print "Error while sending updated playbook: %s" % (
                        str(rcse))
                else:
                    print colorize("Updated playbook for %s:" % project,
                                   color="green")
                    return result
            # elif send_back.lower() == 'd':
            #     orig = reclient.utils.temp_json_blob(pb)
            #     reclient.utils.differ(orig, pb_fp)
            elif send_back.lower() == 'n':
                print colorize("Not sending back. Playbook will be saved in %s until this program is closed." % (
                    pb_fp.name),
                    color="yellow")
                return
            else:
                # You entered in garbage. Start over...
                pass

    def download_playbook(self, save_path, project, pb_id):
        (pb, path) = self._get_playbook(project, pb_id)
        print "Playbook fetched"
        print "Saving playbook to: %s" % save_path
        reclient.utils.save_playbook(pb, save_path)
        print colorize(
            "Success: Playbook %s saved to %s" % (
                pb_id, save_path),
            color="green")

    def upload_playbook(self, source_path, project):
        with open(source_path, 'r') as _source:
            result = self._send_playbook(project, _source)
        _id = colorize(str(result.json()['id']), color="yellow")
        print colorize(
            "Success: Playbook uploaded. ID: %s" % (
                _id),
            color="green")

    def delete_playbook(self, project, pb_id):
        suffix = "%s/playbook/%s/" % (project, pb_id)
        result = self.connector.delete(suffix)
        return result

    def start_deployment(self, project, pb_id):
        suffix = "%s/playbook/%s/deployment/" % (
            project, pb_id)
        result = self.connector.put(suffix)
        try:
            _status = result.json().get('status')
            if _status == 'error':
                raise ReClientDeployError(result)
        except ReClientDeployError, rcde:
            response_msg = rcde.args[0].json()
            print colorize("Error while fetching playbooks for %s:" % project,
                           color="red",
                           background="lightgray")
            print colorize(
                "%s - %s" % (
                    str(rcde),
                    response_msg['message']),
                color="red", background="lightgray")
            return False
        except Exception, e:
            print colorize("Unknown error while starting deployment: %s" %
                           (str(e)),
                           color="red")
        else:
            return result

    def new_playbook(self, project):
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


class ReClientDeployError(ReClientError):
    pass
