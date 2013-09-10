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
import traceback

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
    
    prompt = "H lb>"  # default prompt
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.libplugin = LibLoadBalancers()
        
        # declared Cloud Load-balancers nodes
        self.declared_nodes = []

    def do_EOF(self, line): 
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True

    # ########################################
    # LOAD BALANCERS
    
    def do_create_load_balancer(self, line):
        '''
        create a Cloud Load-balancers load-balancer
        
        name             load-balancer name
        virtual_ip_type  load-balancer virtual ip_type (default:PUBLIC, or SERVICENET)
        port             load-balancer port (default: 80)
        protocol         load-balancer protocol (default: HTTP)
        node_index       index of first node to be added to load-balancer
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (name, virtual_ip_type, port, protocol, node_index) = (None, 'PUBLIC',
                                                               80, 'HTTP', None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            logging.warn("name missing")
            return False
        if 'virtual_ip_type' in d_kv.keys():
            virtual_ip_type = d_kv['virtual_ip_type']
        else:
            logging.warn("portvirtual_ip_type missing, using default value "
                         "'%s'" % virtual_ip_type)
        if 'port' in d_kv.keys():
            port = d_kv['port']
        else:
            logging.warn("port missing, using default value '%s'" % port)
        if 'protocol' in d_kv.keys():
            protocol = d_kv['protocol']
        else:
            logging.warn("protocol missing")
            return False
        if 'node_index' in d_kv.keys():
            node_index = int(d_kv['node_index'])
        else:
            logging.warn("node_index missing")
            return False
        clb = pyrax.cloud_loadbalancers
        if protocol not in clb.protocols:
            logging.warn("protocol '%s' not allowed possible values: " 
                         ', '.join([p for p in clb.protocols]))
            return False
        logging.info('creating load-balancer name:%s, virtual_ip:%s, port:%s,'
                     ' protocol:%s, node_index:%s' %
                     (name, virtual_ip_type, port, protocol, node_index))
        try:
            vip = clb.VirtualIP(type = virtual_ip_type)
            clb.create(name, port = port, protocol = protocol,
                       nodes = [self.declared_nodes.pop(node_index)],
                       virtual_ips = [vip])
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_create_load_balancer(self, text, line, begidx, endidx):
        params = ['name:', 'virtual_ip:', 'port:', 'protocol:', 'node_index']
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
        list load balancers
        '''
        logging.debug("line: %s" % line)
        logging.info("listing cloud load balancers")
        clb = pyrax.cloud_loadbalancers
        pt = PrettyTable(['id', 'name', 'node count', 'protocol',
                          'virtual_ips',
                          'port', 'status', 'algorithm', 'timeout'])
        for lb in clb.list():
            pt.add_row([
                        lb.id, lb.name, lb.nodeCount, lb.protocol,
                        '\n'.join(["%s (%s)" % (i.address, i.type)
                                   for i in lb.virtual_ips]),
                        lb.port, lb.status, lb.algorithm, lb.timeout
                        ])
        pt.align['virtual_ips'] = 'l'
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
        for k, v in lb.get_stats().items():
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
    
    def do_declare_node(self, line):
        '''
        declare Cloud Load-balancers node
        
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
            logging.warn("condition missing, using default value '%s'" % 
                         condition)
        if condition not in ('ENABLED', 'DISABLED', 'DRAINING'):
            logging.warn("condition value '%s' not allowed"
                         "possible values: ENABLED, DISABLED, DRAINING" % 
                         condition)
            return False
        logging.info('declared node address:%s, port:%s, condition:%s' % 
                     (address, port, condition))
        try:
            clb = pyrax.cloud_loadbalancers
            self.declared_nodes.append(clb.Node(address = address, port = port,
                                                condition = condition))
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
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
    
    def do_delete_node(self, line):
        '''
        delete Cloud Load-balancers node from declared_nodes list
        
        index        node index in declared_nodes list
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (index) = (None)
        # parsing parameters
        if 'index' in d_kv.keys():
            index = int(d_kv['index'])
        else:
            logging.warn("index missing")
            return False
        try:
            removed_node = self.declared_nodes.pop(index) 
            logging.info('deleting node index: %d, address:%s, port:%s, condition:%s' % 
                     (index, removed_node.address, removed_node.port,
                      removed_node.condition))
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_delete_node(self, text, line, begidx, endidx):
        params = ['index:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_list_declared_nodes(self, lines):
        '''
        list declared nodes
        '''
        pt = PrettyTable(['index', 'address', 'port', 'condition'])
        ctr = 0
        for n in self.declared_nodes:
            pprint.pprint(n)
            pt.add_row([ctr, n.address, n.port, n.condition])
            ctr += 1
        print pt
    
    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
