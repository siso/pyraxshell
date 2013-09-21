# -*- coding: utf-8 -*-

# This file is part of pyraxshell.
#
# pyraxshell is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyraxshell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyraxshell. If not, see <http://www.gnu.org/licenses/>.

import sys
import subprocess


def show_usage():
    print "pyraxcli <CMD> [, <CMD> ...]"
    print
    print ("python pyraxshell/pyraxcli.py servers, list, EOF, loadbalancers, "
           "list, list_nodes id:81957")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        show_usage()
        sys.exit(0)
    print "pyraxcli starting"
    args =  " ".join([a for a in sys.argv[1:]])
    print args
    commands = args.split(',')
    process = subprocess.Popen(['python', 'pyraxshell'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE
                               )
    for c in commands:
        process.stdin.write("%s\n" % c)
    process.stdin.flush()
    process.stdin.close()
    errcode = process.wait()
    for line in process.stdout:
        print line.rstrip()
    print "pyraxcli -- subprocess error code: %s" % errcode
