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
import pyrax
from prettytable import PrettyTable
import time

class LibServers(object):
    '''
    pyraxshell servers library
    '''
    
    # ########################################
    # SERVERS
    def list_cloudservers(self):
        cs = pyrax.cloudservers
        return cs.list()
    
    def list_cloudservers_flavors(self):
        return pyrax.cloudservers.list_flavors()
    
    def list_cloudservers_images(self):
        return pyrax.cloudservers.list_images()
    
    def create_server(self, name, flavor_id, image_id, poll_time = 30):
        '''
        create a server, wait for completion, 
        aka server status in ('ACTIVE', 'ERROR', 'UNKNOWN')
        
        poll_time    polling time waiting for completion in seconds
        
        return dictionary {name, id, status, adminPass, networks}, None if error
        '''
        statuses = ['ACTIVE', 'ERROR', 'UNKNOWN']
        cs = pyrax.cloudservers
        server = cs.servers.create(name, image_id, flavor_id)
        while server.status not in statuses:
            time.sleep(poll_time)
            server.get()
            logging.info('server \'%s\', status:%s, progress:%s' %
                         (server.name, server.status, server.progress))
        
        if server.status == 'ACTIVE':
            d = {
                'name'      : server.name,
                'id'        : server.id,
                'status'    : server.status,
                'adminPass' : server.adminPass,
                'networks'  : server.networks
                }
            # print info
            pt = PrettyTable(['key', 'value'])
            pt.add_row(['name', d['name']])
            pt.add_row(['id', d['id']])
            pt.add_row(['status', d['status']])
            pt.add_row(['adminPass', d['adminPass']])
            pt.add_row(['network public ipv4', d['networks']['public'][0]])
            pt.add_row(['network public ipv6', d['networks']['public'][1]])
            pt.add_row(['network private ipv4', d['networks']['private'][0]])
            pt.align['key'] = 'l'
            pt.align['value'] = 'l'
            print pt
            # return info
        else:
            logging.error(('cannot create server \'%s\' (status:%s)' %
                           (server.name, server.status)))
            return None
    
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
#                  pt.add_row(['image', self.get_cloudserver_flavor(server.image['id']).name])
                pt.add_row(['flavor', self.get_cloudserver_flavor(server.flavor['id']).name])
#                 pt.add_row(['password', server.get_password()])
                pt.add_row(['progress', server.progress])
#                 pt.add_row(['adminPass', server.get_password()])
                pt.add_row(['network public (ipv4)', server.networks['public'][0]])
                pt.add_row(['network public (ipv6)', server.networks['public'][1]])
                pt.add_row(['network private (ipv4)', server.networks['private'][0]])
                print pt
    
    def get_cloudserver_flavor(self, _id):
        csf = self.list_cloudservers_flavors()
        for f in csf:
            if f.id == _id:
                return f
        return None

    def get_cloudserver_image(self, _id):
        csi = self.list_cloudservers_image()
        for f in csi:
            if f.id == _id:
                return f
        return None
    
    def print_pt_cloudservers(self):
        '''print cloud servers flavors with PrettyTable'''
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
        print pt
    
    def print_pt_cloudservers_flavors(self):
        '''print cloud servers flavors with PrettyTable'''
        csflavors = self.list_cloudservers_flavors()
        pt = PrettyTable(['id', 'name', 'ram', 'swap', 'vcpus'])
        for csf in csflavors:
            pt.add_row([csf.id, csf.name, csf.ram, csf.swap, csf.vcpus])
        print pt

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
            print pt.get_string(sortby=sortby)
        else:
            print pt
