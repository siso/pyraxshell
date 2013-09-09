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

    # ########################################
    # LOAD BALANCERS
    
    def do_list(self, line):
        '''
        list load balancers
        '''
        logging.debug("line: %s" % line)
        logging.info("listing cloud load balancers")
        clb = pyrax.cloud_loadbalancers
        pt = PrettyTable(['id', 'name', 'node count', 'protocol',
                          'port', 'status', 'algorithm', 'timeout'])
        for lb in clb.list():
            pt.add_row([
                        lb.id, lb.name, lb.nodeCount, lb.protocol,
                        lb.port, lb.status, lb.algorithm, lb.timeout
                        ])
        print pt
    
    def do_list_algorithms(self, line):
        '''
        list load balancers algorithms
        '''
        logging.debug("line: %s" % line)
        logging.info("listing cloud load balancers algorithms")
        clb = pyrax.cloud_loadbalancers
        pt = PrettyTable(['name'])
        for alg in clb.algorithms:
            pt.add_row([alg])
        pt.align['name'] = 'l'
        print pt
    
    def do_list_protocols(self, line):
        '''
        list load balancers protocols
        '''
        logging.debug("line: %s" % line)
        logging.info("listing cloud load balancers protocols")
        clb = pyrax.cloud_loadbalancers
        pt = PrettyTable(['name'])
        for p in clb.protocols:
            pt.add_row([p])
        pt.align['name'] = 'l'
        print pt
    
    def do_stats(self, line):
        '''
        list load balancers stats
        
        id    load-balancer id
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id) = (None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            logging.warn("id missing")
            return False
        logging.info("listing cloud load balancers stats")
        lb = self.libplugin.get_instance_by_id(_id)
        pt = PrettyTable(['key', 'value'])
        for k,v in lb.get_stats().items():
            pt.add_row([k, v])
        pt.align['key'] = 'l'
        pt.align['value'] = 'l'
        print pt
    
    def complete_stats(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_virtual_ips(self, line):
        '''
        list load balancers virtual IPs
        
        id    load-balancer id
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id) = (None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            logging.warn("id missing")
            return False
        logging.info("listing cloud load balancer virtual IPs")
        lb = self.libplugin.get_loadbalancer_by_id(_id)
        pprint.pprint(lb)
        pt = PrettyTable(['id', 'type', 'address', 'ip_version'])
        for vip in lb.virtual_ips:
            pt.add_row([vip.id, vip.type, vip.address, vip.ip_version])
        pt.align['id'] = 'l'
        pt.align['address'] = 'l'
        print pt
    
    def complete_virtual_ips(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    # ########################################
    # NODES    
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
