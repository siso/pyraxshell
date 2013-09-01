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

import pyrax
from prettytable import PrettyTable

class LibDatabases(object):
    '''
    pyraxshell database library
    '''
    
    # ########################################
    # DATABASES
    def list_cloud_databases(self):
        return pyrax.cloud_databases.list()
    
    def list_cloud_databases_flavors(self):
        cdb = pyrax.cloud_databases
        return cdb.list_flavors()
    
    def print_pt_cloud_databases(self, sortby='name'):
        '''print my cloud databases with PrettyTable
        
        with 'sortby' data can be sorted by column; if 'raw' is passed, then
        data is printed as it is returned by OpenStack'''
        cdb = self.list_cloud_databases()
        pt = PrettyTable(['id', 'name', 'status'])
        for db in cdb:
            pt.add_row([db.id, db.name, db.status])
        pt.align['name'] = 'l'
        if sortby != None:
            print pt.get_string(sortby=sortby)
        else:
            print pt
    
    def print_pt_cloud_databases_flavors(self, sortby='id'):
        '''print cloud database flavors with PrettyTable
        
        with 'sortby' data can be sorted by column; if 'raw' is passed, then
        data is printed as it is returned by OpenStack'''
        cdbf = self.list_cloud_databases_flavors()
        pt = PrettyTable(['id', 'name', 'ram', 'loaded'])
        for dbf in cdbf:
            pt.add_row([dbf.id, dbf.name, dbf.ram, dbf.loaded])
        pt.align['name'] = 'l'
        if sortby != None:
            print pt.get_string(sortby=sortby)
        else:
            print pt

    # ########################################
    # INSTANCES
    def create_instance(self, name, flavor_id, volume):
        cdb = pyrax.cloud_databases
        return cdb.create(name, flavor_id, volume)
