from reclient.connectors import Connectors
import reclient.utils

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

    def get_all_playbooks(self, project):
        """
        Get all playbooks that match `project`
        """
        project = project.replace(' ', '%20')
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
        return (result.json(), pb_fp)

    def view_file(self, project, pb_id):
        (pb, path) = self._get_playbook(project, pb_id)
        reclient.utils.less_file(path.name)

    def edit_playbook(self, project, pb_id):
        (pb, path) = self._get_playbook(project, pb_id)
        reclient.utils.edit_playbook(pb)
