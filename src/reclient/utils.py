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


import os
from subprocess import call
import tempfile
import json
import yaml
import logging
# import difflib

out = logging.getLogger('reclient')


def cooked_input(msg=""):  # pragma: no cover
    """We need this to test user prompt"""
    return raw_input(msg)


def user_prompt_yes_no(prompt_str=""):
    """Simple re-useable prompt for action confirmation. Adds [y/n]
    suffix automatically.

    Returns True if Yes, False if No
    """
    ret = None
    while ret is None:
        ans = cooked_input(prompt_str + "[y/n]: ")
        if (ans == 'y') or (ans == 'Y'):
            ret = True
        elif (ans == 'n') or (ans == 'N'):
            ret = False
        else:
            continue

    return ret


def serialize(blob, format):
    """
    Serializes a structure.
    """
    if format == 'json':
        return json.dumps(blob, indent=4)
    return yaml.safe_dump(blob)


def deserialize(blob, format):
    """
    Retutns a deserialized structure.
    """
    if format == 'json':
        return json.loads(blob)
    return yaml.safe_load(blob)


def save_playbook(blob, dest, format):
    """Save the temporary playbook, `source` at `path`"""
    with open(dest, 'w') as _dest:
        del blob['id']
        if format == 'json':
            json.dump(blob, _dest, indent=4)
        else:
            yaml.safe_dump(blob, _dest)


def temp_blob(data, format):
    """data is either a string or a hash. Function will 'do the right
thing' either way

format is the format to write with.
"""
    out.debug("tmp_blob received [%s]: %s" % (type(data), str(data)))
    if type(data) in [unicode, str]:
        data = json.loads(data)
    elif type(data) == dict or type(data) == list:
        pass
    else:
        raise ValueError("This isn't something I can work with")

    tmpfile = tempfile.NamedTemporaryFile(mode='w',
                                          suffix=".%s" % format,
                                          prefix="reclient-")
    if format == 'json':
        json.dump(data, tmpfile, indent=4)
    else:
        yaml.safe_dump(data, tmpfile)
    tmpfile.flush()
    return tmpfile

# def differ(orig, new):
#     """Diff two documents and open in 'less'. 'orig' and 'new' should be
#     file pointers"""
#     d = difflib.Differ()


def edit_playbook(blob, format):
    """Edit the playbook object 'blob'.

If 'blob' is an unserialized string, then it is serialized and dumped
(with indenting) out to a temporary file.

If 'blob' is a serialized hash is is dumped out (with indenting) to a
temporary file.

If 'blob' is a file object (like you would get from 'temp_blob')
it is flush()'d.

'format' is either json or yaml.

Once all that is complete, an editor is opened pointing at the path to
the temporary file. After the editor is closed the original (or
instantiated) file handle is returned."""
    EDITOR = os.environ.get('EDITOR', 'emacs')
    callcmd = [EDITOR]
    tmpfile = blob

    # Could be a file we just grabbed with
    # ReClient._get_playbook. Flush it first so we aren't editing an
    # empty file.
    if isinstance(blob, tempfile._TemporaryFileWrapper):
        blob.flush()
    else:
        tmpfile = temp_blob(blob, format)

    try:
        out.debug("Editing with EDITOR=%s" % EDITOR)
        if EDITOR == "emacs":
            # Do not launch in graphical mode
            callcmd.extend(["-nw", tmpfile.name])
        else:
            callcmd.append(tmpfile.name)

        out.debug("Going to launch editor with args: %s" % str(callcmd))

        call(callcmd)
    except OSError:
        # Whatever we called before failed. Try 'vi' as a fallback,
        # then try 'vim'
        out.debug("First call to EDITOR failed. Trying 'vi' explicitly")

        try:
            fallback_call = ['vi', tmpfile.name]
            call(fallback_call)
        except OSError:
            out.debug("Second call to EDITOR failed. Trying 'vim' explicitly")
            try:
                fallback_back_call = ['vim', tmpfile.name]
                call(fallback_back_call)
            except OSError:
                out.info(
                    "Could not launch any editors. Tried: %s, vi, and vim" % (
                        EDITOR))
                return False
    return tmpfile


def less_file(path):
    call(['less', '-X', path])
