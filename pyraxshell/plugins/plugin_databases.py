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
import pyrax
from prettytable import PrettyTable
import traceback

from globals import WARNING, INFO, ERROR, WARN
from plugin import Plugin
from plugins.libdatabases import LibDatabases, InstanceCreatorThread
from utility import kvstring_to_dict

name = 'databases'

def injectme(c):
    setattr(c, 'do_databases', do_databases)
    logging.debug('%s injected' % __file__)

def do_databases(*args):
    Cmd_databases().cmdloop()


class Cmd_databases(Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Manage databases
    '''
    
    prompt = "RS db>"    # default prompt

    def __init__(self):
        Plugin.__init__(self)
        self.libplugin = LibDatabases()
        self.cdb = pyrax.cloud_databases
    
    # ########################################
    # CLOUD DATABASES - INSTANCES
    def do_create_instance(self, line):
        '''
        create a new cloud databases instance
        
        Parameters:
        
        flavor_id    see: list_flavors
        name
        volume       volume size (GiB)
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (name, flavor_id, volume) = (None, None, None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            cmd_out = "name missing"
            self.r(1, cmd_out, WARNING)
            return False
        if 'flavor_id' in d_kv.keys():
            flavor_id = d_kv['flavor_id']
        else:
            cmd_out = "flavor_id missing"
            self.r(1, cmd_out, WARNING)
            return False
        if 'volume' in d_kv.keys():
            volume = d_kv['volume']
        else:
            cmd_out = "volume missing"
            self.r(1, cmd_out, WARNING)
            return False
        try:
            logging.debug('creating database instance - name:%s, flavor_id:%s, '
                          'volume=%s' % (name, flavor_id, volume))
            cdbit = InstanceCreatorThread(name, flavor_id, volume)
            cdbit.setName('CloudDBInstance-%s' % name)
            cdbit.start()
        except:
            tb = traceback.format_exc()
            logging.error(tb)
    
    def complete_create_instance(self, text, line, begidx, endidx):
        params = ['flavor_id:', 'name:', 'volume:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete_instance(self, line):
        '''
        delete a cloud databases instance
        
        Parameters:
        
        flavor_id    see: list_flavors
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
            cmd_out = "id missing"
            self.r(1, cmd_out, WARNING)
            return False
        try:
            db_instance = self.libplugin.get_instance_by_id(_id)
            db_instance.delete()
            cmd_out = 'Cloud Databases instance id:%s deleted' % _id
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_delete_instance(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_list_instances(self, line):
        '''
        list _my_ cloud databases instances
        '''
        logging.info("list my database instances")
        logging.debug("line: %s" % line)
        cdb = pyrax.cloud_databases
        pt = PrettyTable(['id', 'name', 'status', 'hostname', 'created',
                          'ram', 'links'])
        for db in cdb.list():
            pt.add_row([db.id,
                        db.name,
                        db.status,
                        db.hostname,
                        db.created,
                        db.flavor.ram,
                        '\n'.join([l['href'] for l in db.links])])
        pt.align['name'] = 'l'
        pt.align['links'] = 'l'
        self.r(0, pt, INFO)
    
    def do_list_instance_flavors(self, line):
        '''
        list cloud databases instances flavours
        '''
        logging.info("list db flavours")
        logging.debug("    line: %s" % line)
        cdb = pyrax.cloud_databases
        cdbf = cdb.list_flavors()
        pt = PrettyTable(['id', 'name', 'ram', 'loaded'])
        for dbf in cdbf:
            pt.add_row([dbf.id, dbf.name, dbf.ram, dbf.loaded])
        pt.align['name'] = 'l'
        self.r(0, pt, INFO)
    
    def do_list(self, line):
        '''
        list_instances alias
        '''
        return self.do_list_instances(line)
    
    def do_resize_instance(self, line):
        '''
        resize cloud database instance
        
        !: resize ram or volume one at a time
        
        Parameters:
        
        id         instance id
        ram        ram size (MiB)
        volume     volume size (GiB)
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, ram, volume) = (None, None, None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            cmd_out = "instance id missing"
            self.r(1, cmd_out, ERROR)
            return False
        if 'ram' in d_kv.keys():
            ram = d_kv['ram']
        if 'volume' in d_kv.keys():
            volume = d_kv['volume']
        if (ram == None and volume == None) or (ram != None and volume != None):
            cmd_out = 'specify ram or volume'
            self.r(1, cmd_out, WARN)
            return False
        try:
            db_instance = self.libplugin.get_instance_by_id(_id)
            if ram != None:
                db_instance.resize(int(ram))
            if volume != None:
                db_instance.resize_volume(volume)
            cmd_out = 'Cloud Databases instance id:%s resized' %_id
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_resize_instance(self, text, line, begidx, endidx):
        params = ['id:', 'ram:', 'volume:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    # ########################################
    # CLOUD DATABASES - DATABASES
    
    def do_create_database(self, line):
        '''
        create cloud databases 'database'
        
        Parameters:
        
        instance_id          id of instance
        database_name        name of database
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (instance_id, database_name) = (None, None)
        # parsing parameters
        if 'instance_id' in d_kv.keys():
            instance_id = d_kv['instance_id']
        else:
            cmd_out = "instance_id missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'database_name' in d_kv.keys():
            database_name = d_kv['database_name']
        else:
            cmd_out = "database_name missing"
            self.r(1, cmd_out, WARN)
            return False
        try:
            db_instance = self.libplugin.get_instance_by_id(instance_id)
            db_instance.create_database(database_name)
            cmd_out = ('created database_name:%s in '
                       'Cloud Databases instance id:%s,'
                        % (database_name, instance_id))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_create_database(self, text, line, begidx, endidx):
        params = ['instance_id:', 'database_name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete_database(self, line):
        '''
        delete cloud databases 'database'
        
        Parameters:
        
        instance_id          id of instance
        database_name        name of database
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (instance_id, database_name) = (None, None)
        # parsing parameters
        if 'instance_id' in d_kv.keys():
            instance_id = d_kv['instance_id']
        else:
            cmd_out = "instance_id missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'database_name' in d_kv.keys():
            database_name = d_kv['database_name']
        else:
            cmd_out = "database_name missing"
            self.r(1, cmd_out, WARN)
            return False
        try:
            database = self.libplugin.get_database(instance_id, database_name)
            if database == None:
                cmd_out = ('cannot find database name:%s in instance_id:%s' %
                           (database_name, instance_id))
                self.r(1, cmd_out, ERROR)
            else:
                database.delete()
                cmd_out = ('delete database instance - instance_id:%s,'
                           'database_name:%s' % (instance_id, database_name))
                self.r(1, cmd_out, ERROR)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_delete_database(self, text, line, begidx, endidx):
        params = ['instance_id:', 'database_name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_list_databases(self, line):
        '''
        list cloud databases 'database'
        
        Parameters:
        
        instance_id          id of instance
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (instance_id) = (None)
        # parsing parameters
        if 'instance_id' in d_kv.keys():
            instance_id = d_kv['instance_id']
        else:
            cmd_out = "instance_id missing"
            self.r(1, cmd_out, WARN)
            return False
        try:
            logging.debug('listing databases in instance name:%s, id:%s,'
                          % (self.libplugin.get_instance_by_id(instance_id).name,
                             instance_id))
            db_instance = self.libplugin.get_instance_by_id(instance_id)
            pt = PrettyTable(['name'])
            for db in db_instance.list_databases():
                logging.debug("%s" % db.name)
                pt.add_row([db.name])
            self.r(0, pt, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_list_databases(self, text, line, begidx, endidx):
        params = ['instance_id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    # ########################################
    # CLOUD DATABASES - USERS
    
    def do_create_user(self, line):
        '''
        create cloud databases 'user'
        
        Parameters:
        
        instance_id          id of instance
        database_name        name of database
        username
        password
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (instance_id, database_name, username, password) = (None, None, None,
                                                            None)
        # parsing parameters
        if 'instance_id' in d_kv.keys():
            instance_id = d_kv['instance_id']
        else:
            cmd_out = "instance_id missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'database_name' in d_kv.keys():
            database_name = d_kv['database_name']
        else:
            cmd_out = "database_name missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'username' in d_kv.keys():
            username = d_kv['username']
        else:
            cmd_out = "username missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'password' in d_kv.keys():
            password = d_kv['password']
        else:
            cmd_out = "password missing"
            self.r(1, cmd_out, WARN)
            return False
        try:
            db_instance = self.libplugin.get_instance_by_id(instance_id)
            db_instance.create_user(username, password,
                                    database_names = database_name)
            cmd = ('created username:%s, password:%s to instance_id:%s,'
                   'database_name:%s' % (username, password, instance_id,
                                         database_name))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_create_user(self, text, line, begidx, endidx):
        params = ['instance_id:', 'database_name:', 'username:', 'password:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete_user(self, line):
        '''
        delete cloud databases 'user'
        
        Parameters:
        
        instance_id          id of instance
        username
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (instance_id, username) = (None, None)
        # parsing parameters
        if 'instance_id' in d_kv.keys():
            instance_id = d_kv['instance_id']
        else:
            cmd_out = "instance_id missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'username' in d_kv.keys():
            username = d_kv['username']
        else:
            cmd_out = "username missing"
            self.r(1, cmd_out, WARN)
            return False
        try:
            db_instance = self.libplugin.get_instance_by_id(instance_id)
            db_instance.delete_user(username)
            cmd_out = ('deleted username:%s from instance_id:%s' %
                       (username, instance_id))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_delete_user(self, text, line, begidx, endidx):
        params = ['instance_id:', 'username:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_list_users(self, line):
        '''
        list cloud databases 'users'
        
        Parameters:
        
        instance_id          id of instance
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (instance_id) = (None)
        # parsing parameters
        if 'instance_id' in d_kv.keys():
            instance_id = d_kv['instance_id']
        else:
            logging.error("instance_id missing")
            return False
        try:
            logging.info('listing users for instance name:%s, id:%s,'
                          % (self.libplugin.get_instance_by_id(instance_id).name,
                             instance_id))
            db_instance = self.libplugin.get_instance_by_id(instance_id)
            pt = PrettyTable(['databases', 'host', 'name'])
            for user in db_instance.list_users():
                pt.add_row([
                            user.databases,
                            user.host,
                            user.name
                            ])
            self.r(0, pt, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_list_users(self, text, line, begidx, endidx):
        params = ['instance_id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
