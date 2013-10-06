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
import threading
import time

from globals import msg_queue, INFO


class InstanceCreatorThread (threading.Thread):
    '''
    thread to create a Cloud Databases instance
    '''
    
    def __init__(self, _name, flavor_id, volume, poll_time=30):
        '''
        Constructor
        
        _name       Cloud Databases Instance name
        flavor_id   Cloud Databases Instance flavour id
        volume      Cloud Databases Instance volume
        poll_time   polling server creation progress in seconds
        '''
        threading.Thread.__init__(self)
        self._name = _name
        self.flavor_id = flavor_id
        self.volume = volume
        self.poll_time = poll_time
        logging.debug('thread name:%s, instance name:%s, flavor_id:%s,'
                      ' volume:%s'
                      % (self.getName, _name, flavor_id, volume))
        self._terminate = False
    
    def run(self):
        '''
        create a server, wait for completion, 
        aka server status in ('ACTIVE', 'ERROR', 'UNKNOWN')
        
        poll_time    polling time waiting for completion in seconds
        '''
        logging.debug("Starting %s" % self.name)
        statuses = ['ACTIVE', 'ERROR', 'UNKNOWN']
        cdb = pyrax.cloud_databases
        cdbi = cdb.create(self._name, flavor=int(self.flavor_id),
                          volume=self.volume)
        logging.debug('polling Cloud database instance creation progress (%d)' % self.poll_time)
        while cdbi.status not in statuses:
            if self._terminate == True:
                logging.debug("terminating thread %s" % self.name)
                return
            time.sleep(1)
            if int(time.time()) % self.poll_time == 0:
                # mitigate polling server creation progress 
                cdbi.get()
                logging.debug('server \'%s\', status:%s' % (cdbi.name,
                                                            cdbi.status))
            msg_queue.put('db instance \'%s\': %s' % (cdbi.name, cdbi.status))
        cdbi.get()
        msg = 'server \'%s\', status:%s' % (cdbi.name, cdbi.status)
        self.r(0, msg, INFO)


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
