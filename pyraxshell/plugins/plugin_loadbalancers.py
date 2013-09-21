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
from utility import kvstring_to_dict, is_ipv4
import pyrax
import pyrax.exceptions as exc
from prettytable import PrettyTable
import pprint
import traceback
import plugins

name = 'loadbalancers'

def injectme(c):
    setattr(c, 'do_loadbalancers', do_loadbalancers)
    logging.debug('%s injected' % __file__)

def do_loadbalancers(*args):
    Cmd_loadbalancers().cmdloop()

from plugins.libloadbalancers import LibLoadBalancers
from plugin import Plugin

class Cmd_loadbalancers(Plugin, cmd.Cmd):
    '''
    pyrax shell POC - load-balancers module
    '''
    
    prompt = "RS lb>"  # default prompt
    
    def __init__(self):
        Plugin.__init__(self)
        self.libplugin = LibLoadBalancers()
        
        # declared Cloud Load-balancers nodes
        self.declared_nodes = []

    # ########################################
    # LOAD BALANCERS
    
    def do_add_node(self, line):
        '''
        add a node to load-balancer
        
        id            load-balancer id
        node_index    node id within load-balancer
        '''
#TODO --
        logging.info('TO BE IMPLEMENTED')
    
    def complete_add_node(self, text, line, begidx, endidx):
        params = ['id:', 'node_index']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
        
    def do_create_load_balancer(self, line):
        '''
        create a Cloud Load-balancers load-balancer
        
        name             load-balancer name
        virtual_ip_type  load-balancer virtual ip_type (default:PUBLIC, or SERVICENET)
        port             load-balancer port (default: 80)
        protocol         load-balancer protocol (default: HTTP)
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (name, virtual_ip_type, port, protocol) = (None, 'PUBLIC', 80, 'HTTP')
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
        clb = pyrax.cloud_loadbalancers
        if protocol not in clb.protocols:
            logging.warn("protocol '%s' not allowed possible values: " 
                         ', '.join([p for p in clb.protocols]))
            return False
        logging.info('creating load-balancer name:%s, virtual_ip:%s, port:%s,'
                     ' protocol:%s, nodes:[%s]' %
                     (name, virtual_ip_type, port, protocol,
                      ",".join(["%s" % n for n in self.declared_nodes])))
        try:
            vip = clb.VirtualIP(type = virtual_ip_type)
            clb.create(name, port = port, protocol = protocol,
                       nodes = self.declared_nodes,
                       virtual_ips = [vip])
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_create_load_balancer(self, text, line, begidx, endidx):
        params = ['name:', 'virtual_ip:', 'port:', 'protocol:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete(self, line):
        '''
        delete Cloud Load-balancers load-balancer
        
        id             load-balancer id
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
        logging.info('deleting load-balancer id:%s' % _id)
        try:
            clb = pyrax.cloud_loadbalancers
            lb = clb.get(_id)
            lb.delete()
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_delete(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_details(self, line):
        '''
        load-balancer details
        
        id            load-balancer id
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
        logging.info("Cloud load-balancer id:%s details" % _id)
        try:
            pt = PrettyTable(['key', 'value'])
# TODO --   #
            # if I do 'lb = clb.get(_id)' then lb does not have 'nodeCount'
            # attribute. Why?
            #clb = pyrax.cloud_loadbalancers
            lb = self.libplugin.get_loadbalancer_by_id(_id)
            #
            pt.add_row(['id', _id])
            pt.add_row(['node count', lb.nodeCount])
            pt.align['key'] = 'l'
            pt.align['value'] = 'l'
            print pt
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_details(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_get_usage(self, line):
        '''
        show Cloud Load-balancer usage
        
        Please note that usage statistics are very fine-grained, with a record
        for every hour that the load balancer is active.
        
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
        logging.info("Cloud load-balancer id:%s usage" % _id)
        lb = self.libplugin.get_loadbalancer_by_id(_id)
        try:
            d_usage = lb.get_usage()['loadBalancerUsageRecords']
#             print d_usage
            pt = PrettyTable(['averageNumConnections',
                              'averageNumConnectionsSsl',
                              'endTime',
                              'id',
                              'incomingTransfer',
                              'incomingTransferSsl',
                              'numPolls',
                              'numVips',
                              'outgoingTransfer',
                              'outgoingTransferSsl',
                              'sslMode',
                              'startTime',
                              'vipType'
                              ])
            for record in d_usage:
#                 print record.values()
                pt.add_row([record['averageNumConnections'],
                            record['averageNumConnectionsSsl'],
                            record['endTime'],
                            record['id'],
                            record['incomingTransfer'],
                            record['incomingTransferSsl'],
                            record['numPolls'],
                            record['numVips'],
                            record['outgoingTransfer'],
                            record['outgoingTransferSsl'],
                            record['sslMode'],
                            record['startTime'],
                            record['vipType']
                            ])
            print pt
        except:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_get_usage(self, text, line, begidx, endidx):
        params = ['id:']
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
    
    def do_list_nodes(self, line):
        '''
        list load-balancer nodes
        
        id            load-balancer id
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
        logging.info("listing cloud load-balancer id:%s nodes" % _id)
        clb = pyrax.cloud_loadbalancers
        pt = PrettyTable(['index', 'type', 'condition', 'id', 'address', 'port',
                          'weight'])
        try:
            lb = clb.get(_id)
            ctr = 0
            for n in lb.nodes:
                pt.add_row([
                            ctr, n.type, n.condition, n.id, n.address,
                            n.port, n.weight
                            ])
                ctr += 1
            pt.align['virtual_ips'] = 'l'
            print pt
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_list_nodes(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
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
    
    def do_list_virtual_ips(self, line):
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
        try:
            clb = pyrax.cloud_loadbalancers
            lb = clb.get(_id)
            pprint.pprint(lb)
            pt = PrettyTable(['id', 'type', 'address', 'ip_version'])
            for vip in lb.virtual_ips:
                pt.add_row([vip.id, vip.type, vip.address, vip.ip_version])
            pt.align['id'] = 'l'
            pt.align['address'] = 'l'
            print pt
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_list_virtual_ips(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_stats(self, line):
        '''
        list load balancers stats
        
        id    load-balancer id
        '''
        logging.info("currently does not work")
        return False
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
        lb = self.libplugin.get_loadbalancer_by_id(_id)
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
    
    def do_update(self, line):
        '''
        update Cloud Load-balancer attributes 
        
        id    load-balancer id
        name
        algorithm
        protocol
        halfClosed
        port
        timeout
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, name, algorithm, protocol, halfClosed, port, timeout) = (
         (None, None, None, None, None, None, None))
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            logging.warn("id missing")
            return False
        if 'name' in d_kv.keys():
            name = d_kv['name']
            logging.debug("name: %s" % name)
        if 'algorithm' in d_kv.keys():
            algorithm = d_kv['algorithm']
            logging.debug("algorithm: %s" % algorithm)
        if 'protocol' in d_kv.keys():
            protocol = d_kv['protocol']
            logging.debug("protocol: %s" % protocol)
        if 'halfClosed' in d_kv.keys():
            halfClosed = d_kv['halfClosed']
            logging.debug("halfClosed: %s" % halfClosed)
        if 'port' in d_kv.keys():
            port = d_kv['port']
            logging.debug("port: %s" % port)
        if 'timeout' in d_kv.keys():
            timeout = d_kv['timeout']
            logging.debug("timeout: %s" % timeout)
        logging.info("updating Cloud load-balancer id:%s (%s)" % (_id, d_kv))
        lb = self.libplugin.get_loadbalancer_by_id(_id)
        del d_kv['id']  # remove 'id' and use d_kv as kargs
        # check params
        k_domain = ['name', 'algorithm', 'protocol', 'halfClosed', 'port',
                    'timeout']
        for k in d_kv.keys():
            if k not in k_domain:
                logging.warn('found invalid param \'%s\'' % k)
                del d_kv[k]
        if len(d_kv) == 0:
            logging.warn('no params to update Cloud load-balancer')
            return False
        try:
            lb.update(**d_kv)
        except:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_update(self, text, line, begidx, endidx):
        params = ['id:', 'name:', 'algorithm:', 'protocol:', 'halfClosed:',
                  'port:', 'timeout:']
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
        condition        ENABLED, DISABLED, DRAINING (default: ENABLED)
        port             port (default: 80)
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
    
    def complete_declare_node(self, text, line, begidx, endidx):
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
        delete the node from its load balancer
        
        id            load-balancer id
        node_id       id of node to delete 
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, node_id) = (None, None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            logging.warn("id missing")
            return False
        if 'node_id' in d_kv.keys():
            node_id = d_kv['node_id']
        else:
            logging.warn("node_id missing")
            return False
        logging.info("deleting node id:%s from Cloud load-balancer id:%s" %
                     (_id, node_id))
        try:
            node = self.libplugin.get_node_by_id(_id, node_id)
#TODO -- print node details
            node.delete()
            logging.info("node id:%s from Cloud load-balancer id:%s deleted" %
                     (_id, node_id))
        except Exception:
            logging.info("error deleting node id:%s from Cloud load-balancer "
                         "id:%s deleted" % (_id, node_id))
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_delete_node(self, text, line, begidx, endidx):
        params = ['id:', 'node_id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_undeclare_node(self, line):
        '''
        undeclare Cloud Load-balancers node from declared_nodes list
        
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
        except IndexError:
            logging.error('no declared node with index:%d' % index)
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_undeclare_node(self, text, line, begidx, endidx):
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
    
    def do_set_node_condition(self, line):
        '''
        set node condition
        
        id            load-balancer id
        node_id       id of node to delete
        condition    can be in one of 3 "conditions": ENABLED, DISABLED, and DRAINING
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, node_id, condition) = (None, None, None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            logging.warn("id missing")
            return False
        if 'node_id' in d_kv.keys():
            node_id = d_kv['node_id']
        else:
            logging.warn("node_id missing")
            return False
        logging.info("deleting node id:%s from Cloud load-balancer id:%s" %
                     (_id, node_id))
        if 'condition' in d_kv.keys():
            condition = d_kv['condition']
        else:
            logging.warn("condition missing")
            return False
        condition_domain = ['ENABLED', 'DISABLED', 'DRAINING']
        if condition not in condition_domain:
            logging.warn('condition can be: \'%s\', not \'%s\'' %
                         (', '.join([c for c in condition_domain]), condition))
            return False
        logging.info("setting node id:%s condition:%s in Cloud load-balancer"
                     "id:%s" % (_id, condition, node_id))
        try:
            node = self.libplugin.get_node_by_id(_id, node_id)
            node.condition = condition
            node.update()
            logging.info("node id:%s condition:%s in Cloud load-balancer id:%s"
                         % (_id, condition, node_id))
        except Exception:
            logging.info("error setting node id:%s condition:%s in Cloud"
                         "load-balancer id:%s" % (_id, condition, node_id))
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_set_node_condition(self, text, line, begidx, endidx):
        params = ['id:', 'node_id:', 'condition:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
