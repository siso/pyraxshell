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
from plugins.libcloudfiles import LibCloudfiles  # @UnresolvedImport
from utility import kv_dict_to_pretty_table, objects_to_pretty_table  # @UnresolvedImport

name = 'cloudfiles'

def injectme(c):
    setattr(c, 'do_cloudfiles', do_cloudfiles)
    logging.debug('%s injected' % __file__)

def do_cloudfiles(*args):
    Cmd_cloudfiles().cmdloop()


class Cmd_cloudfiles(Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Manage CloudFiles module
    '''
    
    prompt = "RS cloudfiles>"    # default prompt

    def __init__(self):
        Plugin.__init__(self)
        self.libplugin = LibCloudfiles()
        self.cf = pyrax.cloudfiles
    
    # ########################################
    # DEFAULT METHODS
    
    def do_list(self, line):
        '''
        set default list method
        '''
        self.do_list_container(line)
    
    # ########################################
    # CONTAINER
    
    def do_list_container(self, line):
        '''
        list container
        
        @param all    displays all the properties
        '''
        cc = self.cf.get_all_containers()
        # properties to be displayed
        props = ['name', 'object_count', 'total_bytes']
        if self.arg == 'all':
            props = ['name', 'object_count', 'total_bytes',
                    'cdn_enabled', 'cdn_ios_uri', 'cdn_log_retention',
                    'cdn_ssl_uri', 'cdn_streaming_uri', 'cdn_ttl', 'cdn_uri',]
        # create a PrettyTable obj with those columns
        pt = objects_to_pretty_table(cc, props)
        # PrettyTable style
        pt.align['name'] = 'l' 
        for c in props[1:]:
            pt.align[c] = 'r'
        pt.sortby = 'name'
        #
#         print pt
        self.r(0, pt, INFO)
    
    def complete_list_container(self, text, line, begidx, endidx):
        params = ['all']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions


    # ########################################
    # METADATA
    
    def do_get_accout_metadata(self, line):
        '''
        overall usage for Cloud Files
        '''
        try:
            data = self.cf.get_account_metadata()
            pt = kv_dict_to_pretty_table(data)
            self.r(0, str(pt), INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False

    def do_set_account_metadata(self, line):
        '''
        set account metadata
        
        @param metadata_values  as 'key1:value1 .. keyn:valuen'
        '''
        try:
            self.cf.set_account_metadata(self.kvarg)
            cmd_out = "metadata set"
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False
    
    