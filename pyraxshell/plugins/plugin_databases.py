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
from plugins.libdatabases import LibDatabases
from utility import kvstring_to_dict

name = 'databases'

def injectme(c):
    setattr(c, 'do_databases', do_databases)
    logging.debug('%s injected' % __file__)

def do_databases(*args):
    Cmd_Databases().cmdloop()


class Cmd_Databases(cmd.Cmd):
    '''
    pyrax shell POC - Manage databases
    '''
    
    prompt = "H db>"    # default prompt

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.libplugin = LibDatabases()

    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True
    
    def do_create_instance(self, line):
        '''
        create a new cloud database instance
        
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
            logging.warn("name missing")
            return False
        if 'flavor_id' in d_kv.keys():
            flavor_id = d_kv['flavor_id']
        else:
            logging.warn("flavor_id missing")
            return False
        if 'volume' in d_kv.keys():
            volume = d_kv['volume']
        else:
            logging.warn("volume missing")
            return False
        try:
            self.libplugin.create_instance(name, flavor_id, volume)
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst           # __str__ allows args to printed directly
    
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
    
    def do_exit(self, *args):
        return True

    def do_list(self, line):
        '''
        list _my_ databases
        '''
        logging.info("list my db")
        logging.debug("line: %s" % line)
        self.libplugin.print_pt_cloud_databases()
    
    def do_list_flavors(self, line):
        '''
        list database flavors
        '''
        logging.info("list db flavors")
        logging.debug("line: %s" % line)
        self.libplugin.print_pt_cloud_databases_flavors()
    
    def do_create(self, line):
        '''
        create a new database
        ''' 
        logging.info('NOT IMPLEMENTED YET')

    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
