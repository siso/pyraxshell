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
from libpyraxshell import Libpyraxshell
import logging
from utility import kvstring_to_dict, is_ipv4
import pyrax
import pyrax.exceptions as exc
from prettytable import PrettyTable
import pprint
from plugins.libloadbalancers import LibLoadBalancers

name = 'loadbalancers'

def injectme(c):
    setattr(c, 'do_loadbalancers', do_loadbalancers)
    logging.debug('%s injected' % __file__)

def do_loadbalancers(*args):
    Cmd_LoadBalancers().cmdloop()


class Cmd_LoadBalancers(cmd.Cmd):
    '''
    pyrax shell POC - load-balancers module
    '''
    
    prompt = "H lb>"    # default prompt
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.libplugin = LibLoadBalancers()

    def do_EOF(self, line): 
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True

    def do_add_node(self, line):
        # WORKING...
        '''
        add nodes to load-balancer 
        
        loadbalancer     load-balancer name
        address          IP address
        port             port (default: 80)
        condition        ENABLED, DISABLED, DRAINING (default: ENABLED)
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (address, port, condition) = (None, 80, 'ENABLED')
        # parsing parameters
        if 'address' in d_kv.keys():
            address = d_kv['address']
        else:
            logging.warn("address missing")
            return False
        if 'port' in d_kv.keys():
            port = d_kv['port']
        else:
            logging.warn("port missing, using default value '%s'" % port)
        if 'condition' in d_kv.keys():
            condition = d_kv['condition']
        else:
            logging.warn("condition missing")
            logging.warn("condition missing, using default value '%s'" %
                         condition)
        logging.debug(pyrax.identity.is_authenticated)
        clb = pyrax.cloud_loadbalancers
        clb.list()
    
    def complete_add_node(self, text, line, begidx, endidx):
        params = ['address:', 'condition:', 'port:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions

    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
