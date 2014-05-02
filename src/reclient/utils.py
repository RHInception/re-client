import os
from subprocess import call
import tempfile
import json

def temp_json_blob(data):
    """data is either a string or a hash. Function will 'do the right
thing' either way"""
    if type(data) in [unicode, str]:
        data = json.loads(data)
    elif type(data) == dict:
        pass
    else:
        raise ValueError("This isn't something I can work with")

    tmpfile = tempfile.NamedTemporaryFile(mode='w',
                                          suffix=".json",
                                          delete=False,
                                          prefix="reclient-")
    json.dump(data, tmpfile, indent=4)
    tmpfile.flush()
    return tmpfile

def edit_playbook(blob):
    """Edit the playbook object 'blob'.

If 'blob' is an unserialized string, then it is serialized and dumped
(with indenting) out to a temporary file.

If 'blob' is a serialized hash is is dumped out (with indenting) to a
temporary file.

If 'blob' is a file object (like you would get from 'temp_json_blob')
it is flush()'d.

Once all that is complete, an editor is opened pointing at the path to
the temporary file. After the editor is closed the original (or
instantiated) file handle is returned."""
    EDITOR = os.environ.get('EDITOR', 'emacs')
    callcmd = [EDITOR]
    tmpfile = blob

    if isinstance(blob, tempfile._TemporaryFileWrapper):
        blob.flush()
    else:
        tmpfile = temp_json_blob(blob)

    try:
        if EDITOR == "emacs":
            # Do not launch in graphical mode
            callcmd.extend(["-nw", tmpfile.name])
        else:
            callcmd.append(tmpfile.name)

        print "Going to launch editor with args: %s" % str(callcmd)

        call(callcmd)
    except OSError, e:
        callcmd.extend(tmpfile.name)
        call(callcmd)

    return tmpfile

def less_file(path):
    call(['less', path])
