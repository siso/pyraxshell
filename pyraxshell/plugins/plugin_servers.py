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
from utility import kvstring_to_dict
from plugins.libservers import LibServers

name = 'servers'

def injectme(c):
    setattr(c, 'do_servers', do_servers)
    logging.debug('%s injected' % __file__)

def do_servers(*args):
    Cmd_Servers().cmdloop()


class Cmd_Servers(cmd.Cmd):
    '''
    pyrax shell POC - Manage servers module
    '''
    
    prompt = "H servers>"    # default prompt

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.libplugin = LibServers()

    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True
        
    def do_create(self, line):
        '''
        create a new server
        
        Parameters:
        
        flavor_id    see: list_flavors
        image_id     see: list_images
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
            logging.warn("name missing")
            return False
        if 'flavor_id' in d_kv.keys():
            flavor_id = d_kv['flavor_id']
        else:
            logging.warn("flavor_id missing")
            return False
        if 'image_id' in d_kv.keys():
            image_id = d_kv['image_id']
        else:
            logging.warn("image_id missing")
            return False
        try:
            self.libplugin.create_server(name, flavor_id, image_id)
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly

    def complete_create(self, text, line, begidx, endidx):
        params = ['flavor_id', 'image_id', 'name']
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
        delete server
        
        Parameters:
        
        id i.e.: H servers> delete name:XXX
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
            logging.warn("server id is missing")
            return False
        logging.info('deleting server id:%s' % _id)
        self.libplugin.delete_server(_id)
    
    def do_details(self, line):
        '''
        display server details
        
        Parameters:
        
        id or name
        
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
        if '_id' in d_kv.keys():
            _id = d_kv['_id']
        if (id, name) == (None, None):
            logging.warn("server id and name missing, specify at least one")
            return False         
        try:
            self.libplugin.details_server(_id, name)
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly

    def complete_details(self, text, line, begidx, endidx):
        params = ['id', 'name']
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
        self.libplugin.print_pt_cloudservers()
    
    def do_list_flavors(self, line):
        '''
        list servers flavors
        '''
        logging.info("list servers")
        logging.debug("line: %s" % line)
        self.libplugin.print_pt_cloudservers_flavors()
    
    def do_list_images(self, line):
        '''
        list servers images
        '''
        logging.info("list servers")
        logging.debug("line: %s" % line)
        self.libplugin.print_pt_cloudservers_images()

    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
