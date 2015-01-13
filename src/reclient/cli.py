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
    # People just need a little reminder...
    print ""
    print colorize("   re-client is readline enabled!",
                   color="lgreen")

    print colorize("   Use up/down keys to go through history",
                   color="lgreen")

    print """
0) Get all playbooks ever (if you're authorized)
1) Get all playbooks for a project
2) Get a single playbook for a project
3) Update a playbook
4) Delete a playbook
5) Create a new playbook
6) Start a deployment
7) Download a playbook
8) Upload a playbook
9) Quit"""

######################################################################
# REPL
######################################################################


def repl(args):
    """Read. Evaluate. Print. Loop"""
    rclient = RC(debug=args.debug, format=args.format)
    while True:
        cmds()
        try:
            action = int(raw_input(
                colorize("command>> ",
                         color="yellow")))
        except KeyboardInterrupt:
            raise SystemExit
        except ValueError, e:
            bad_input = e.args[0].split(':')[1].replace("'", '').strip()
            if bad_input.lower() == 'q':
                raise SystemExit
            else:
                print colorize("Invalid option. Try again.", color="red")
                continue
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
            if args.id is None:
                pb_id = raw_input("Playbook ID: ")
            else:
                pb_id = args.id
            rclient.start_deployment(project, pb_id)
        elif action == 7:
            # Download a playbook
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            if args.id is None:
                pb_id = raw_input("Playbook ID: ")
            else:
                pb_id = args.id
            save_path = raw_input("Save as: ")
            rclient.download_playbook(save_path, project, pb_id)
        elif action == 8:
            # Upload a playbook
            if args.project is None:
                project = raw_input("Project: ")
            else:
                project = args.project
            source_path = raw_input("Source file: ")
            rclient.upload_playbook(source_path, project)
        elif action == 9:
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

    out.info("* What is the port of your re-rest endpoint?")
    _port = 443
    out.info("* Press enter to accept https as the default: %s" % (
        _port))

    input_port = raw_input("Port: ")

    if input_port.strip() == "":
        config_port = _port
    else:
        config_port = int(input_port)

    print "Port is %s" % config_port
    out.info("* What is the name you use to authenticate with?")
    _username = pwd.getpwuid(os.getuid())[0]
    out.info("* Press enter to accept the default: %s" % (
        _username))

    input_username = raw_input("Username: ")

    if input_username.strip() == "":
        config_username = _username
    else:
        config_username = input_username

    input_kerberos = raw_input("Use Kerberos? (y/n): ").upper()
    if input_kerberos == 'Y':
        input_kerberos = True
    else:
        input_kerberos = False

    with open(conf_file, 'w') as _c_write:
        if config_port == 443:
            _new_config = {
                "baseurl": "https://" + config_hostname,
                "username": config_username
            }
        elif config_port == 80:
            _new_config = {
                "baseurl": "http://" + config_hostname,
                "username": config_username
            }
        else:
            _new_config = {
                "baseurl": "http://{}:{}".format(config_hostname, config_port),
                "username": config_username
            }
        _new_config['use_kerberos'] = input_kerberos
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
    parser.add_argument('-f', '--format', required=False,
                        default='yaml', choices=('yaml', 'json'),
                        help='Set playbook format (Default: yaml)')

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

if __name__ == '__main__':
    cli()
