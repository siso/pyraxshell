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
import pyrax
import traceback

from globals import *  # @UnusedWildImport
from plugin import Plugin
from plugins.libservers import LibServers, ServerCreatorThread
from utility import kvstring_to_dict

name = 'servers'

def injectme(c):
    setattr(c, 'do_servers', do_servers)
    logging.debug('%s injected' % __file__)

def do_servers(*args):
    Cmd_servers().cmdloop()


class Cmd_servers(Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Manage servers module
    '''
    
    prompt = "RS servers>"    # default prompt

    def __init__(self):
        Plugin.__init__(self)
        self.libplugin = LibServers()

    # ########################################
    # SERVER    
    def do_change_password(self, line):
        '''
        reboot server
        
        id        server id
        password  new password
        '''
#         cmd_in = "%s %s" % (inspect.stack()[0][3][3:], line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, password) = (None, None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        if (id, name) == (None, None):
            cmd_out = "server id missing"
            self.r(1, cmd_out, WARNING)
            return False
        if 'password' in d_kv.keys():
            password = d_kv['password']
        else:
            cmd_out = "new password missing"
            self.r(1, cmd_out, WARNING)
            return False
        try:
            s = self.libplugin.get_by_id(_id)
        except IndexError:
            cmd_out = 'server id:%s not found' % _id
            self.r(1, cmd_out, WARNING)
            return False
        try:
            if s.status == 'ACTIVE':
                s.change_password(password)
                cmd_out = 'changed root password on server id:%s, name:%s' % (_id, s.name)
                self.r(0, cmd_out, INFO)
            else:
                cmd_out = 'cannot change root password on server id:%s, name:%s' % (_id, s.name)
                self.r(1, cmd_out, ERROR)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_change_password(self, text, line, begidx, endidx):
        params = ['id:', 'password:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_create(self, line):
        '''
        create a new server
        
        Parameters:
        
        flavor_id        see: list_flavors
        image_id         see: list_images
        name
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (name, flavor_id, image_id) = (None, None, None)
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
        if 'image_id' in d_kv.keys():
            image_id = d_kv['image_id']
        else:
            cmd_out = "image_id missing"
            self.r(1, cmd_out, WARNING)
            return False
        try:
            # create ServerCreatorTread
            sct = ServerCreatorThread(name, flavor_id, image_id, poll_time = 30)
            # start thread
            sct.setName('server-%s' % name)
            sct.start()
            # completion message printed by thread in libservers
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_create(self, text, line, begidx, endidx):
        params = ['flavor_id:', 'image_id:', 'name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
#TODO --
        last_token = line.split()[-1]
        logging.debug("last_token: %s" % last_token)
        if last_token == 'flavor_id:':
            logging.debug("auto-complete flavour")
        elif last_token == 'image_id:':
            logging.debug("auto-complete image_id")
        elif last_token == 'name:':
            logging.debug("auto-complete name")
        return completions
    
    def do_delete(self, line):
        '''
        delete server
        
        It is safer deleting a CloudServer by id, as different servers
        could have the same name.
        
        Parameters:
        id     server id
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        _id = None
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        if _id == None:
            cmd_out = "server id is missing"
            self.r(1, cmd_out, WARNING)
            return False
        self.libplugin.delete_server(_id)
        cmd_out = 'deleting server id:%s' % _id
        self.r(0, cmd_out, INFO)
    
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
        display server details
        id or name must be specified
        
        Parameters:
        
        id        server id
        name      server name
        
        i.e.: H servers> details name:foo
        ''' 
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, name) = (None, None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        if (_id, name) == (None, None):
            cmd_out = "server id and name missing, specify at least one"
            self.r(1, cmd_out, WARNING)
            return False         
        try:
            # output in libservers
            self.libplugin.details_server(_id, name)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False

    def complete_details(self, text, line, begidx, endidx):
        params = ['id:', 'name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_exit(self,*args):
        return True

    def do_list(self, line):
        '''
        list my servers
        '''
        logging.info("list my servers")
        logging.debug("line: %s" % line)
        # output in libservers
        self.libplugin.print_pt_cloudservers()
    
    def do_list_flavors(self, line):
        '''
        list servers flavors
        '''
        logging.info("list servers")
        logging.debug("line: %s" % line)
        # output in libservers
        self.libplugin.print_pt_cloudservers_flavors()
    
    def do_list_images(self, line):
        '''
        list servers images
        '''
        logging.info("list servers")
        logging.debug("line: %s" % line)
        # output in libservers
        self.libplugin.print_pt_cloudservers_images()
    
    def do_reboot(self, line):
        '''
        reboot server
        
        id        server id to reboot
        type      'cold' or 'hard' reboot
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, _type) = (None, 'cold')
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        if (id, name) == (None, None):
            cmd_out = "server id missing, cannot continue"
            self.r(1, cmd_out, WARNING)
            return False
        if 'type' in d_kv.keys():
            _type = d_kv['type']
        else:
            logging.warn("reboot type not specified, defaulting to 'cold'")
        _type = str.upper(_type)
        if _type != 'COLD' and _type != 'HARD':
            cmd_out = "reboot type can be: cold or hard, not \'%s\'" % _type
            self.r(1, cmd_out, WARNING)
            return False
        try:
            s = self.libplugin.get_by_id(_id)
            self.r(0, cmd_out, INFO)
        except IndexError:
            cmd_out = 'cannot find server identified with id:%s' % _id
            self.r(1, cmd_out, ERROR)
            return False
        try:
            if s.status == 'ACTIVE':
                s.reboot(_type)
                cmd_out = '%s rebooted server id:%s' % (_type, _id)
                self.r(0, cmd_out, INFO)
            else:
                cmd_out = ('cannot reboot server id:%s, status:%s' %
                           (_id, s.status))
                self.r(1, cmd_out, ERROR)
                return False
                
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_reboot(self, text, line, begidx, endidx):
        params = ['id:', 'type:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions

    # ########################################
    # SERVER SNAPSHOTS
    #
    # "qui pro quo": server snapshots are called 'snapshot' when using API
    #                and 'images' on the web Control Panel, which might lead to
    #                confusion, as images are also called (on the web Control
    #                Panel and in the API) the 'initial images' to use to spin
    #                up servers
    def do_take_snapshots(self, line):
        '''
        create an image of a server
        
        id               server id
        snapshot_name    name of the snapshot to be taken
#TODO   metadata         key-value pairs metadata
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_id, snapshot_name) = (None, None)
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        else:
            cmd_out = "server id missing, cannot continue"
            self.r(1, cmd_out, WARNING)
            return False
        if 'snapshot_name' in d_kv.keys():
            snapshot_name = d_kv['snapshot_name']
        else:
            cmd_out = "snapshot_name missing, cannot continue"
            self.r(1, cmd_out, WARNING)
            return False
        try:
            s = self.libplugin.get_by_id(_id)
        except IndexError:
            cmd_out = 'cannot find server identified by id:%s' % _id
            self.r(1, cmd_out, ERROR)
            return False
        try:
            s.create_image(snapshot_name)
            cmd_out = ('took snapshot name:%s of server id:%s' %
                       (snapshot_name, _id))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
    
    def complete_take_snapshots(self, text, line, begidx, endidx):
        params = ['id:', 'snapshot_name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions    

    def do_delete_snapshot(self, line):
        '''
        delete snapshot
        
        Parameters:
        id     snapshot id
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        _id = None
        # parsing parameters
        if 'id' in d_kv.keys():
            _id = d_kv['id']
        if _id == None:
            cmd_out = "snapshot id is missing"
            self.r(1, cmd_out, WARNING)
            return False
        try:
            cs = pyrax.cloudservers
            snapshot = [ss for ss in cs.list_snapshots() if ss.id == _id][0]
            snapshot.delete()
            cmd_out = 'deleted snapshot id:%s' % snapshot.id
            self.r(0, cmd_out, INFO)
        except IndexError:
            cmd_out = 'cannot find snapshot identified by id:%s' % _id
            self.r(1, cmd_out, ERROR)
            return False
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
    
    def complete_delete_snapshot(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions   
    
    def do_list_snapshots(self, line):
        '''
        list snapshots
        '''
        logging.info("list snapshots")
        logging.debug("line: %s" % line)
        try:
            cs = pyrax.cloudservers
            pt = PrettyTable(['id', 'name', 'created', 'minDisk', 'minRam',
                              'progress', 'server id', 'status', 'updated'])
            for ss in cs.list_snapshots():
                pt.add_row([
                                ss.id,
                                ss.name,
                                ss.created,
                                ss.minDisk,
                                ss.minRam,
                                ss.progress,
                                ss.server['id'],
                                ss.status,
                                ss.updated
                            ])
            pt.align['id'] = 'l'
            pt.align['name'] = 'l'
            self.r(0, str(pt), INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
