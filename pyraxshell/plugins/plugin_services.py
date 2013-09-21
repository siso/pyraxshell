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
from utility import kvstring_to_dict

import pprint
import pyrax
from prettytable import PrettyTable

from plugin import Plugin
from plugins.libservices import LibServices

name = 'services'

def injectme(c):
    setattr(c, 'do_services', do_services)
    logging.debug('%s injected' % __file__)
#     
#     logging.debug('c.get_names(): %s' % c.get_names())

def do_services(*args):
#     logging.debug("line: %s" % line)
    Cmd_services().cmdloop()


class Cmd_services(Plugin, cmd.Cmd):
    """
    pyraxshell - Services plugin 
    """
    prompt = "RS %s>" % name    # default prompt
    
    def __init__(self):
        Plugin.__init__(self)
        self.libplugin = LibServices()

    # ########################################
    # ENDPOINTS
    def do_endpoints(self, line):
        '''
        list endponts
        
        raw            True to print raw JSON response (default: False)
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (raw) = (None)
        # parsing parameters
        if 'raw' in d_kv.keys():
            raw = d_kv['raw']
            if str.lower(raw) == 'true':
                raw = True
            else:
                raw = False
        if not raw:
            pt = PrettyTable(['service', 'name', 'endpoints'])
            for k,v in pyrax.identity.services.items():  # @UndefinedVariable
#                 print "service: %s" % k
#                 print "\tname: %s" % v['name']
#                 print "\tendpoints: %s" % v['endpoints']
                ep = ''
                for k1,v1 in v['endpoints'].items():
#                     print "\t\t%s --> %s" % (k1, v1)
                    ep += "\n".join("%s: %s --> %s" % (k1, k2, v2)
                                    for k2,v2 in v1.items())
                pt.add_row([k, v['name'], ep])
            pt.align['service'] = 'l'
            pt.align['name'] = 'l'
            pt.align['endpoints'] = 'l'
            print pt
        else:
            pprint.pprint(pyrax.identity.services)
    
    def complete_endpoints(self, text, line, begidx, endidx):
        params = ['raw:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_list(self, line):
        '''
        list services
        '''
        logging.info("\n".join([s for s in pyrax.services]))
    
    def do_test(self, line):
        '''
        provide credentials and authenticate
        '''
        logging.debug("TEST PLUGIN -- do_test")
        logging.debug("line: %s" % line)
