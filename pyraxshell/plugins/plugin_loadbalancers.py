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
from prettytable import PrettyTable
import pprint
import pyrax
import traceback

from pyraxshell.globals import INFO, ERROR, WARN
from pyraxshell.utility import kvstring_to_dict, is_ipv4
from pyraxshell.plugins.libloadbalancers import LibLoadBalancers
import pyraxshell.plugins.plugin


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    '''
    pyrax shell POC - load-balancers module
    '''

    prompt = "RS load-balancers>"  # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
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
# TODO --
        logging.info('TO BE IMPLEMENTED')

    def complete_add_node(self, text, line, begidx, endidx):
        params = ['id:', 'node_index']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_create_load_balancer(self, line):
        '''
        create a Cloud Load-balancers load-balancer

        name             load-balancer name
        virtual_ip_type  load-balancer virtual ip_type (default:PUBLIC, or
                         SERVICENET)
        port             load-balancer port (default: 80)
        protocol         load-balancer protocol (default: HTTP)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'name', 'required': True},
            {'name': 'virtual_ip_type', 'default': 'PUBLIC'},
            {'name': 'port', 'default': 80},
            {'name': 'protocol', 'default': 'HTTP'},
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        clb = pyrax.cloud_loadbalancers
        if self.kvarg['protocol'] not in clb.protocols:
            cmd_out = ("protocol '%s' not allowed possible values: "
                       ', '.join([p for p in clb.protocols]))
            self.r(1, cmd_out, WARN)
            return False
        try:
            vip = clb.VirtualIP(type=self.kvarg['virtual_ip_type'])
            clb.create(self.kvarg['name'], port=self.kvarg['port'],
                       protocol=self.kvarg['protocol'],
                       nodes=self.declared_nodes,
                       virtual_ips=[vip])
            cmd_out = ('created load-balancer name:%s, virtual_ip:%s, port:%s,'
                      ' protocol:%s, nodes:[%s]' %
                      (self.kvarg['name'], self.kvarg['virtual_ip_type'],
                       self.kvarg['port'], self.kvarg['protocol'],
                       ",".join(["%s" % n for n in self.declared_nodes])))
            self.r(0, cmd_out, INFO)
        except Exception:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_create_load_balancer(self, text, line, begidx, endidx):
        params = ['name:', 'virtual_ip:', 'port:', 'protocol:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_delete(self, line):
        '''
        delete Cloud Load-balancers load-balancer

        id             load-balancer id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            clb = pyrax.cloud_loadbalancers
            lb = clb.get(self.kvarg['id'])
            lb.delete()
            cmd_out = 'deleted load-balancer id:%s' % self.kvarg['id']
            self.r(0, cmd_out, INFO)
        except Exception:
            tb = traceback.format_exc()
            logging.error(tb)

    def complete_delete(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_details(self, line):
        '''
        load-balancer details

        id            load-balancer id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            pt = PrettyTable(['key', 'value'])
# TODO --   #
            # if I do 'lb = clb.get(_id)' then lb does not have 'nodeCount'
            # attribute. Why?
            # clb = pyrax.cloud_loadbalancers
            lb = self.libplugin.get_loadbalancer_by_id(self.kvarg['id'])
            #
            pt.add_row(['id', self.kvarg['id']])
            pt.add_row(['node count', lb.nodeCount])
            pt.align['key'] = 'l'
            pt.align['value'] = 'l'
            self.r(0, str(pt), INFO)
        except Exception:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_details(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_get_usage(self, line):
        '''
        show Cloud Load-balancer usage

        Please note that usage statistics are very fine-grained, with a record
        for every hour that the load balancer is active.

        id    load-balancer id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'flavor_id', 'required': True},
            {'name': 'name', 'required': True},
            {'name': 'volume', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        lb = self.libplugin.get_loadbalancer_by_id(self.kvarg['id'])
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
            self.r(0, str(pt), INFO)
        except:
            tb = traceback.format_exc()
            logging.error(tb)

    def complete_get_usage(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
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
        self.r(0, str(pt), INFO)

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
        self.r(0, str(pt), INFO)

    def do_list_nodes(self, line):
        '''
        list load-balancer nodes

        id            load-balancer id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck({'name': 'id', 'required': True})
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        clb = pyrax.cloud_loadbalancers
        pt = PrettyTable(['index', 'type', 'condition', 'id', 'address',
                          'port', 'weight'])
        try:
            lb = clb.get(self.kvarg['id'])
            ctr = 0
            for n in lb.nodes:
                pt.add_row([
                            ctr, n.type, n.condition, n.id, n.address,
                            n.port, n.weight
                            ])
                ctr += 1
            pt.align['virtual_ips'] = 'l'
            self.r(0, str(pt), INFO)
        except Exception:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_list_nodes(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
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
        self.r(1, pt, ERROR)

    def do_list_virtual_ips(self, line):
        '''
        list load balancers virtual IPs

        id    load-balancer id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck({'name': 'id', 'required': True})
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            clb = pyrax.cloud_loadbalancers
            lb = clb.get(self.kvarg['id'])
            pprint.pprint(lb)
            pt = PrettyTable(['id', 'type', 'address', 'ip_version'])
            for vip in lb.virtual_ips:
                pt.add_row([vip.id, vip.type, vip.address, vip.ip_version])
            pt.align['id'] = 'l'
            pt.align['address'] = 'l'
            self.r(0, str(pt), INFO)
        except Exception:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_list_virtual_ips(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_stats(self, line):
        '''
        list load balancers stats

        id    load-balancer id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck({'name': 'id', 'required': True})
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        lb = self.libplugin.get_loadbalancer_by_id(self.kvarg['id'])
        pt = PrettyTable(['key', 'value'])
        for k, v in lb.get_stats().items():
            pt.add_row([k, v])
        pt.align['key'] = 'l'
        pt.align['value'] = 'l'
        self.r(1, pt, INFO)

    def complete_stats(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
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
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'name', 'required': True},
            {'name': 'algorithm', 'required': True},
            {'name': 'protocol', 'required': True},
            {'name': 'halfClose', 'required': True},
            {'name': 'port', 'required': True},
            {'name': 'timeout', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        lb = self.libplugin.get_loadbalancer_by_id(self.kvarg['id'])
        d_kv = self.kvarg
        _id = self.kvarg['id']
        del d_kv['id']  # remove 'id' and use d_kv as kargs
        # check params
        k_domain = ['name', 'algorithm', 'protocol', 'halfClosed', 'port',
                    'timeout']
        for k in d_kv.keys():
            if k not in k_domain:
                logging.warn('found invalid param \'%s\'' % k)
                del d_kv[k]
        if len(d_kv) == 0:
            cmd_out = 'no params to update Cloud load-balancer'
            self.r(1, cmd_out, ERROR)
            return False
        try:
            lb.update(**d_kv)
            cmd_out = "updated Cloud load-balancer id:%s (%s)" % (_id, d_kv)
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_update(self, text, line, begidx, endidx):
        params = ['id:', 'name:', 'algorithm:', 'protocol:', 'halfClosed:',
                  'port:', 'timeout:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
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
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'address', 'required': True},
            {'name': 'condition', 'required': True},
            {'name': 'port', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok
        # additional checks
        if self.kvarg['condition'] not in ('ENABLED', 'DISABLED', 'DRAINING'):
            cmd_out = ("condition value '%s' not allowed"
                         "possible values: ENABLED, DISABLED, DRAINING" %
                         self.kvarg['condition'])
            self.r(1, cmd_out, WARN)
            return False
        try:
            clb = pyrax.cloud_loadbalancers
            self.declared_nodes.append(clb.Node(address=self.kvarg['address'],
                                        port=self.kvarg['port'],
                                        condition=self.kvarg['condition']))
            cmd_out = ('declared node address:%s, port:%s, condition:%s' %
                       (self.kvarg['address'], self.kvarg['port'],
                        self.kvarg['condition']))
            self.r(0, cmd_out, INFO)
        except Exception:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_declare_node(self, text, line, begidx, endidx):
        params = ['address:', 'condition:', 'port:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_delete_node(self, line):
        '''
        delete the node from its load balancer

        id            load-balancer id
        node_id       id of node to delete
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'node_id', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            node = self.libplugin.get_node_by_id(self.kvarg['id'],
                                                 self.kvarg['node_id'])
# TODO -- print node details
            node.delete()
            cmd_out = ("node id:%s from Cloud load-balancer id:%s deleted" %
                       (self.kvarg['id'], self.kvarg['node_id']))
            self.r(0, cmd_out, INFO)
        except Exception:
            logging.error("error deleting node id:%s from Cloud load-balancer "
                         "id:%s deleted" % (self.kvarg['id'],
                                            self.kvarg['node_id']))
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_delete_node(self, text, line, begidx, endidx):
        params = ['id:', 'node_id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_undeclare_node(self, line):
        '''
        undeclare Cloud Load-balancers node from declared_nodes list

        index        node index in declared_nodes list
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck({'name': 'index', 'required': True})
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            removed_node = self.declared_nodes.pop(self.kvarg['index'])
            logging.info('deleting node index: %d, address:%s, port:%s, '
                         'condition:%s' % (self.kvarg['index'],
                                           removed_node.address,
                                           removed_node.port,
                                           removed_node.condition))
        except IndexError:
            cmd_out = 'no declared node with index:%d' % self.kvarg['index']
            self.r(1, cmd_out, ERROR)
        except Exception:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_undeclare_node(self, text, line, begidx, endidx):
        params = ['index:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
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
        self.r(0, str(pt), INFO)

    def do_set_node_condition(self, line):
        '''
        set node condition

        id            load-balancer id
        node_id       id of node to delete
        condition     can be in one of 3 "conditions": ENABLED, DISABLED, and
                      DRAINING
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'node_id', 'required': True},
            {'name': 'condition', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok
        # additional checks
        condition_domain = ['ENABLED', 'DISABLED', 'DRAINING']
        if self.kvarg['condition'] not in condition_domain:
            cmd_out = ('condition can be: \'%s\', not \'%s\'' %
                       (', '.join([c for c in condition_domain]),
                        self.kvarg['condition']))
            self.r(1, cmd_out, WARN)
            return False
        try:
            node = self.libplugin.get_node_by_id(self.kvarg['id'],
                                                 self.kvarg['node_id'])
            node.condition = self.kvarg['condition']
            node.update()
            cmd_out = ("set node id:%s condition:%s in Cloud Load-balancer "
                       "id:%s" % (self.kvarg['id'], self.kvarg['condition'],
                                  self.kvarg['node_id']))
            self.r(0, cmd_out, INFO)
        except Exception:
            logging.info("error setting node id:%s condition:%s in Cloud"
                         "load-balancer id:%s" % (self.kvarg['id'],
                                                  self.kvarg['condition'],
                                                  self.kvarg['node_id']))
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_set_node_condition(self, text, line, begidx, endidx):
        params = ['id:', 'node_id:', 'condition:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions
