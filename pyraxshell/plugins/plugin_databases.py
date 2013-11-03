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

from pyraxshell.globals import INFO, ERROR, WARN
from pyraxshell.plugins.libdatabases import LibDatabases, InstanceCreatorThread
import pyraxshell.plugins.plugin


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Manage databases
    '''
    
    prompt = "RS db>"    # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
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
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name':'flavor_id', 'required':True},
            {'name':'name', 'required':True},
            {'name':'volume', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            logging.debug('creating database instance - name:%s, flavor_id:%s, '
                          'volume=%s' % (self.kvarg['name'],
                                         self.kvarg['flavor_id'],
                                         self.kvarg['volume']))
            cdbit = InstanceCreatorThread(self.kvarg['name'],
                                          self.kvarg['flavor_id'],
                                          self.kvarg['volume'])
            cdbit.setName('CloudDBInstance-%s' % self.kvarg['name'])
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
        
        id        Cloud Databases instance id
        ''' 
        retcode, retmsg = self.kvargcheck(
            {'name':'id', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        try:
            db_instance = self.libplugin.get_instance_by_id(self.kvarg['id'])
            db_instance.delete()
            cmd_out = ('Cloud Databases instance id:%s deleted' %
                       self.kvarg['id'])
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
        self.r(0, str(pt), INFO)
    
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
        self.r(0, str(pt), INFO)
    
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
        retcode, retmsg = self.kvargcheck(
            {'name':'id', 'required':True},
            {'name':'ram', 'required':True},
            {'name':'volume', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        if ((self.kvarg['ram'] == None and self.kvarg['volume'] == None) or
            (self.kvarg['ram'] != None and self.kvarg['volume'] != None)):
            cmd_out = 'specify ram or volume'
            self.r(1, cmd_out, WARN)
            return False
        try:
            db_instance = self.libplugin.get_instance_by_id(self.kvarg['id'])
            if self.kvarg['ram'] != None:
                db_instance.resize(int(self.kvarg['ram']))
            if self.kvarg['volume'] != None:
                db_instance.resize_volume(self.kvarg['volume'])
            cmd_out = 'instance id:%s resized' % self.kvarg['id']
            self.r(0, cmd_out, INFO)
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
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name':'instance_id', 'required':True},
            {'name':'database_name', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            db_instance = (
                self.libplugin.get_instance_by_id(self.kvarg['instance_id']))
            db_instance.create_database(self.kvarg['database_name'])
            cmd_out = ('created database_name:%s in '
                       'Cloud Databases instance id:%s,'
                        % (self.kvarg['database_name'],
                           self.kvarg['instance_id']))
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
        retcode, retmsg = self.kvargcheck(
            {'name':'instance_id', 'required':True},
            {'name':'database_name', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            database = (
                self.libplugin.get_database(self.kvarg['instance_id'],
                                            self.kvarg['database_name']))
            if database == None:
                cmd_out = ('cannot find database name:%s in instance_id:%s' %
                           (self.kvarg['database_name'],
                            self.kvarg['instance_id']))
                self.r(1, cmd_out, ERROR)
            else:
                database.delete()
                cmd_out = ('delete database instance - instance_id:%s,'
                           'database_name:%s' %
                           (self.kvarg['instance_id'],
                            self.kvarg['database_name']))
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
        retcode, retmsg = self.kvargcheck(
            {'name':'instance_id', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            logging.debug('listing databases in instance name:%s, id:%s,'
                          % (self.libplugin.get_instance_by_id(
                                self.kvarg['instance_id']).name,
                             self.kvarg['instance_id']))
            db_instance = (
                self.libplugin.get_instance_by_id(self.kvarg['instance_id']))
            pt = PrettyTable(['name'])
            for db in db_instance.list_databases():
                logging.debug("%s" % db.name)
                pt.add_row([db.name])
            self.r(0, str(pt), INFO)
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
        retcode, retmsg = self.kvargcheck(
            {'name':'instance_id', 'required':True},
            {'name':'database_name', 'required':True},
            {'name':'username', 'required':True},
            {'name':'password', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            db_instance = (
                self.libplugin.get_instance_by_id(self.kvarg['instance_id']))
            db_instance.create_user(self.kvarg['username'],
                                    self.kvarg['password'],
                                database_names = self.kvarg['database_name'])
            cmd_out = ('created username:%s, password:%s to instance_id:%s,'
                       'database_name:%s' % (self.kvarg['username'],
                                             self.kvarg['password'],
                                             self.kvarg['instance_id'],
                                             self.kvarg['database_name']))
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
        retcode, retmsg = self.kvargcheck(
            {'name':'instance_id', 'required':True},
            {'name':'username', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            db_instance = (
                self.libplugin.get_instance_by_id(self.kvarg['instance_id']))
            db_instance.delete_user(self.kvarg['username'])
            cmd_out = ('deleted username:%s from instance_id:%s' %
                       (self.kvarg['username'], self.kvarg['instance_id']))
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
        retcode, retmsg = self.kvargcheck(
            {'name':'instance_id', 'required':True}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            logging.info('listing users for instance name:%s, id:%s,'
                         % (self.libplugin.get_instance_by_id(
                                self.kvarg['instance_id']).name,
                                self.kvarg['instance_id']))
            db_instance = (self.libplugin.get_instance_by_id(
                            self.kvarg['instance_id']))
            pt = PrettyTable(['databases', 'host', 'name'])
            for user in db_instance.list_users():
                pt.add_row([
                            user.databases,
                            user.host,
                            user.name
                            ])
            self.r(0, str(pt), INFO)
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
