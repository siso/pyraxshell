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

import logging
from prettytable import PrettyTable
import pyrax
import threading
import time

from pyraxshell.globals import msg_queue, INFO, ERROR
from pyraxshell.plugins.lib import Lib
from pyraxshell.utility import get_ip_family, get_uuid, l


class ServerCreatorThread (threading.Thread):
    '''
    thread to create a CouldServers
    '''

    def __init__(self, name, flavor_id, image_id, poll_time,
                 threadID=get_uuid()):
        '''
        Constructor

        name        CloudServer name
        flavor_id   CloudServer flavour id
        image_id    CloudServer image id
        poll_time   polling server creation progress in seconds
        '''
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.flavor_id = flavor_id
        self.image_id = image_id
        self.poll_time = poll_time
        logging.debug('thread id:%s, server name:%s, flavor_id:%s, image_id:%s'
                      % (threadID, name, flavor_id, image_id))
        # 'terminate' causes the thread to stop
        self._terminate = False

    def run(self):
        '''
        create a server, wait for completion,
        aka server status in ('ACTIVE', 'ERROR', 'UNKNOWN')

        poll_time    polling time waiting for completion in seconds
        '''
        logging.debug("Starting %s" % self.threadID)
        statuses = ['ACTIVE', 'ERROR', 'UNKNOWN']
        cs = pyrax.cloudservers
        server = cs.servers.create(self.name, self.image_id, self.flavor_id)
        logging.debug('polling server creation progress (%d)' % self.poll_time)
        while server.status not in statuses:
            if self._terminate == True:
                logging.debug("terminating thread %s" % self.name)
                return
            time.sleep(1)
            if int(time.time()) % self.poll_time == 0:
                # mitigate polling server creation progress
                server.get()
                logging.debug('server \'%s\', status:%s, progress:%s' %
                          (server.name, server.status, server.progress))
            msg_queue.put('server \'%s\': %s %s' %
                          (server.name, server.status, server.progress))
        if server.status == 'ACTIVE':
            d = {
                'name': server.name,
                'id': server.id,
                'status': server.status,
                'adminPass': server.adminPass,
                'networks': server.networks
                }
            # print info
            pt = PrettyTable(['key', 'value'])
            pt.add_row(['name', d['name']])
            pt.add_row(['id', d['id']])
            pt.add_row(['status', d['status']])
            pt.add_row(['adminPass', d['adminPass']])
            for srv_net in d['networks']['public']:
                pt.add_row(['network public (%s)' % get_ip_family(srv_net),
                            srv_net])
            for srv_net in server.networks['private']:
                pt.add_row(['network private (%s)' % get_ip_family(srv_net),
                            srv_net])
            pt.align['key'] = 'l'
            pt.align['value'] = 'l'
            l('', 0, str(pt), INFO)
            print
            # return info
        else:
            cmd_out = ('Error. Cannot create server \'%s\' (status:%s)' %
                       (server.name, server.status))
            msg_queue.put(cmd_out)
            l('', 1, cmd_out, ERROR)
            return None
        logging.debug("Exiting %s" % self.name)

    @property
    def terminate(self):
        return self._terminate

    @terminate.setter
    def terminate(self, value=True):
        self._terminate = value


class LibServers(Lib):
    '''
    pyraxshell servers library
    '''

    # ########################################
    # SERVERS
    def get_by_id(self, server_id):
        '''
        return a CloudServer object specified by id
        '''
        cs = pyrax.cloudservers
        return [s for s in cs.list() if s.id == server_id][0]

    def list_cloudservers(self):
        cs = pyrax.cloudservers
        return cs.list()

    def list_cloudservers_flavors(self):
        return pyrax.cloudservers.list_flavors()

    def list_cloudservers_images(self):
        return pyrax.cloudservers.list_images()

    def delete_server(self, _id=None, name=None):
        cs = pyrax.cloudservers
        server = cs.servers.get(_id)
        server.delete()

    def details_server(self, _id=None, name=None):
        cs = self.list_cloudservers()
        for server in cs:
            if server.id == _id or server.name == name:
                pt = PrettyTable(['key', 'value'])
#                 for csf in self.list_cloudservers_flavors():
#                     pt.add_row([csf.id, csf.name, csf.minDisk, csf.minRam])
#                 pt.align['key'] = 'r'
                pt.align['value'] = 'l'
#TODO -- use the same technique with the other part of the library
                # print server attributes with introspection    <=== <===
                attrs_to_show = ['status', 'id']
                for a in attrs_to_show:
                    pt.add_row([a, getattr(server, a)])
#TODO -- display image info
#                  pt.add_row(['image',
#                    self.get_cloudserver_flavor(server.image['id']).name])
                pt.add_row(['flavor',
                            self.
                            get_cloudserver_flavor(server.flavor['id']).name])
#                 pt.add_row(['password', server.get_password()])
                pt.add_row(['progress', server.progress])
#                 pt.add_row(['adminPass', server.get_password()])
                for srv_net in server.networks['public']:
                    pt.add_row(['network public (%s)' % get_ip_family(srv_net),
                                srv_net])
                for srv_net in server.networks['private']:
                    pt.add_row(['network private (%s)' %
                                get_ip_family(srv_net), srv_net])
                pt.add_row(['created on', server.created])
                self.r(0, str(pt), INFO)

    def get_cloudserver_flavor(self, _id):
        csf = self.list_cloudservers_flavors()
        for f in csf:
            if f.id == _id:
                return f
        return None

    def get_cloudserver_image(self, _id):
        csi = self.list_cloudservers_images()
        for f in csi:
            if f.id == _id:
                return f
        return None

    def pt_cloudservers(self):
        '''cloud servers list with PrettyTable'''
        cs = self.list_cloudservers()
        pt = PrettyTable(['id', 'name', 'status', 'progress', 'flavor id',
                          'flavor'])
        for csf in cs:
            try:
                pt.add_row([csf.id, csf.name, csf.status, csf.progress,
                            csf.flavor['id'],
                            # it seems that iterating this request slows down a
                            # lot, maybe caching flavors?
                            self.get_cloudserver_flavor(csf.flavor['id']).name
                            ])
            except AttributeError:
                logging.warn('cannot fetch info of id:\'%s\' name:\'%s\'' %
                             (csf.id, csf.name))
                pt.add_row([csf.id, csf.name, csf.status, '-',
                            csf.flavor['id'],
                            # it seems that iterating this request slows down a
                            # lot, maybe caching flavors?
                            self.get_cloudserver_flavor(csf.flavor['id']).name
                            ])
        pt.get_string(sortby='name')
        pt.align['name'] = 'l'
        return pt

    def print_pt_cloudservers_flavors(self):
        '''print cloud servers flavors with PrettyTable'''
        csflavors = self.list_cloudservers_flavors()
        pt = PrettyTable(['id', 'name', 'ram', 'swap', 'vcpus'])
        for csf in csflavors:
            pt.add_row([csf.id, csf.name, csf.ram, csf.swap, csf.vcpus])
        self.r(0, str(pt), INFO)

    def print_pt_cloudservers_images(self, sortby='name'):
        '''print cloud servers images with PrettyTable

        with 'sortby' data can be sorted by column; if 'raw' is passed, then
        data is printed as it is returned by OpenStack'''
        csflavors = self.list_cloudservers_images()
        pt = PrettyTable(['id', 'name', 'minDisk', 'minRam'])
        for csf in csflavors:
            pt.add_row([csf.id, csf.name, csf.minDisk, csf.minRam])
        pt.align['name'] = 'l'
        if sortby != None:
            self.r(0, pt.get_string(sortby=sortby), INFO)
        else:
            self.r(0, str(pt), INFO)
