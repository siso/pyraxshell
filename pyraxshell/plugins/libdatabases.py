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
import logging

class LibDatabases(object):
    '''
    pyraxshell database library
    '''
    
    # ########################################
    # CLOUD DATABASES - INSTANCES
    def get_instance_by_id(self, instance_id):
        '''
        return cloud databases instance specified by id
        '''
        cdb = pyrax.cloud_databases
        try:
            return [cdbi for cdbi in cdb.list() if cdbi.id == instance_id][0]
        except IndexError:
            logging.error('cannot find cloud databases instance id:%s' %
                          instance_id)
            return None
        except:
            logging.error('error searching cloud databases instance by id:%s' %
                          instance_id)
            return None
    
    def get_instance_flavor_by_id(self, flavor_id):
        '''
        return cloud databases instance flavour by id
        '''
        cdb = pyrax.cloud_databases
        return [f for f in cdb.list_flavors() if f.flavor.id == flavor_id][0]

    # ########################################
    # CLOUD DATABASES - DATABASES
    def get_database(self, instance_id, database_name):
        '''
        return cloud databases database
        '''
        instance = self.get_instance_by_id(instance_id)
        if instance == None:
            return None
        else:
            try:
                return [db for db in instance.list_databases()
                        if db.name == database_name][0]
            except IndexError:
                return None
            except:
                logging.error('cannot find database name:%s in instance_id:%s' %
                              (database_name, instance_id))
                return None
