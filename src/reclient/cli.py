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


import readline
from reclient import ReClient as RC
from reclient.colorize import colorize
import reclient
import os
import argparse
import atexit
import logging
import json
import pwd

######################################################################
# Setup configuration files and readline
######################################################################
conf_file = os.path.expanduser('~/.reclient.conf')
readline.parse_and_bind("tab: complete")
try:
    histfile = os.path.expanduser('~/.reclienthist')
    readline.read_history_file(histfile)
except IOError:
    pass

######################################################################
# REPL header
######################################################################


def cmds():
    print """
0) Get all playbooks ever
1) Get all playbooks for a project
2) Get a single playbook for a project
3) Update a playbook
4) Delete a playbook
5) Create a new playbook
6) Start a deployment
7) Quit"""

######################################################################
# REPL
######################################################################


def repl(args):
    """Read. Evaluate. Print. Loop"""
    rclient = RC(debug=args.debug)
    while True:
        cmds()
        try:
            action = int(raw_input(
                colorize("command>> ",
                         color="yellow")))
        except KeyboardInterrupt, ke:
            raise ke
        except:
            continue

        if action == 0:
            # ALL PLAYBOOKS
            rclient.get_all_playbooks_ever()
        elif action == 1:
            # ALL PLAYBOOKS FOR A PROJECT
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            rclient.get_all_playbooks(project)
        elif action == 2:
            # GET A SINGLE PLAYBOOK FOR A PROJECT
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            if args.id is None:
                pb_id = raw_input("Playbook ID: ")
            else:
                pb_id = args.id
            rclient.view_file(project, pb_id)
        elif action == 3:
            # UPDATE A PLAYBOOK
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            if args.id is None:
                pb_id = raw_input("Playbook ID: ")
            else:
                pb_id = args.id
            rclient.edit_playbook(project, pb_id)
        elif action == 4:
            # DELETE A PLAYBOOK
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            if args.id is None:
                pb_id = raw_input("Playbook ID: ")
            else:
                pb_id = args.id
            rclient.delete_playbook(project, pb_id)
        elif action == 5:
            # CREATE A NEW PLAYBOOK
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            rclient.new_playbook(project)
        elif action == 6:
            # START A DEPLOYMENT
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            rclient.start_deployment(project)
        elif action == 7:
            # Quit
            raise SystemExit

######################################################################
# (re)configure reclient
######################################################################


def config_reclient(out):
    try:
        with open(conf_file, 'r') as _c:
            _config = json.load(_c)
    except Exception:
        out.warn("Could not parse %s for configuration variables" % (
            conf_file))
        reclient.reclient_config = first_time_setup(out)
    else:
        if type(_config) == dict:
            if 'baseurl' in _config \
               and 'username' in _config:
                reclient.reclient_config = _config
    return reclient.reclient_config


def first_time_setup(out):
    out.info("Running first-time setup now:")
    out.info("* What is the hostname of your re-rest endpoint?")
    config_hostname = raw_input("HOSTNAME: ")

    out.info("* What is the name you use to authenticate with?")
    _username = pwd.getpwuid(os.getuid())[0]
    out.info("* Press enter to accept the default: %s" % (
        _username))
    input_username = raw_input("Username: ")

    if input_username.strip() == "":
        config_username = _username
    else:
        config_username = input_username

    with open(conf_file, 'w') as _c_write:
        _new_config = {
            "baseurl": "http://" + config_hostname + ":8000",
            "username": config_username
        }
        json.dump(_new_config, _c_write, indent=4)
    return _new_config

######################################################################
# Main entry point
######################################################################


def cli():
    """Entry point from the /bin/re-client command

Parses/updates client configuration via config_reclient, parses
command line options. Launches the REPL.
"""
    parser = argparse.ArgumentParser(
        description='Release Engine Client Utility')
    parser.add_argument('-d', '--debug', action='store_true',
                        default=False, help='Enable REST debugging')
    parser.add_argument('-p', '--project', required=False,
                        default=None, help='Set default project')
    parser.add_argument('-i', '--id', required=False,
                        default=None, help='Set default playbook ID')
    args = parser.parse_args()

    out = logging.getLogger('reclient')
    if args.debug:
        _level = 'DEBUG'
    else:
        _level = 'INFO'

    out.setLevel(_level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    out.addHandler(handler)
    out.debug("Logging set to: %s" % _level)

    config_reclient(out)

    atexit.register(readline.write_history_file, histfile)

    banner = """
 _ __ ___        ___| (_) ___ _ __ | |_
| '__/ _ \_____ / __| | |/ _ \ '_ \| __|
| | |  __/_____| (__| | |  __/ | | | |_
|_|  \___|      \___|_|_|\___|_| |_|\__|
"""
    print colorize(banner, color="green")

    repl(args)
