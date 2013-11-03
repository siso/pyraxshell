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

import cmd
import logging
import pprint
from prettytable import PrettyTable
import pyrax

from pyraxshell.globals import INFO, ERROR
import pyraxshell.plugins.plugin
from pyraxshell.plugins.libservices import LibServices
from pyraxshell.utility import kvstring_to_dict


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    """
    pyraxshell - Services plugin
    """
    prompt = "RS services>"  # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
        self.libplugin = LibServices()

    # ########################################
    # ENDPOINTS
    def do_endpoints(self, line):
        '''
        list endponts

        raw            True to print raw JSON response (default: False)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'raw', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        # parsing parameters
        if 'raw' in self.kvarg.keys():
            raw = self.kvarg['raw']
            if str.lower(raw) == 'true':
                raw = True
            else:
                raw = False
        if not raw:
            pt = PrettyTable(['service', 'name', 'endpoints'])
            for k, v in pyrax.identity.services.items():  # @UndefinedVariable
                ep = ''
                for k1, v1 in v['endpoints'].items():
#                     print "\t\t%s --> %s" % (k1, v1)
                    ep += "\n".join("%s: %s --> %s" % (k1, k2, v2)
                                    for k2, v2 in v1.items())
                pt.add_row([k, v['name'], ep])
            pt.align['service'] = 'l'
            pt.align['name'] = 'l'
            pt.align['endpoints'] = 'l'
            self.r(0, pt, INFO)
        else:
            cmd_out = pprint.pformat(pyrax.identity.services)
            self.r(0, cmd_out, INFO)

    def complete_endpoints(self, text, line, begidx, endidx):
        params = ['raw:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_list(self, line):
        '''
        list services
        '''
        logging.info("\n".join([s for s in pyrax.services]))
