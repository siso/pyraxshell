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
import logging  # @UnusedImport
import os.path  # @UnusedImport
from utility import *  # @UnusedWildImport
import imp
# import plugins  # @UnusedImport
from configuration import Configuration
from plugins.plugin import Plugin

class Cmd_Pyraxshell(Plugin, cmd.Cmd):
    """
    pyrax shell POC
    
    Beware that additional 'do_*' methods might be added at run-time from
    'plugins.plugin_*' modules
    """
    
    prompt = "RS>"    # default prompt
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        # plug-ins
        self.plugin_names = list()
        self.load_plugins()
        # cmd as singleton
        self.cfg = Configuration.Instance()  # @UndefinedVariable

    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True
    
    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')
    
    def do_exit(self, line):
        '''
        EOF alias
        '''
        return self.do_EOF(line)
    
    def do_list(self, line):
        '''
        '''
        logging.info('nothing to list here')
    
    def do_quit(self, line):
        '''
        EOF alias
        '''
        return self.do_EOF(line)
    
    # ########################################
    # MAIN

    def do_credits(self, line):
        '''
        give credits
        '''
        _credits = '''
pyraxshell - Copyright (c) 2013, Simone Soldateschi - All rights reserved.

author:   Simone Soldateschi
email:    simone.soldateschi@gmail.com
homepage: https://github.com/siso/pyraxshell
license:  GPLv3 or later (see LICENSE)
'''
        logging.info(_credits)
    
    def do_license(self, line):
        '''
        display pyraxshell license
        '''
        l = '''
pyraxshell is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyraxshell is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyraxshell. If not, see <http://www.gnu.org/licenses/>.
'''
        logging.info(l)
    
    def do_list_plugins(self, line):
        '''
        list loaded plugins
        '''
        l = sorted(self.plugin_names)
        logging.info("loaded plugins: %s" % ', '.join([p for p in l]))
    
    def do_reload_plugins(self, line):
        '''
        manually load plugins
        '''
        self.unload_plugins('')
        self.load_plugins()
    
    def unload_plugins(self, line):
        '''
        list loaded plugins
        '''
        logging.debug(dir(self))
        logging.debug('unloading plug-ins')
        for i in range(len(self.plugin_names)):  # @UnusedVariable
            p = 'do_%s' % self.plugin_names.pop()
            delattr(self, p)
            logging.debug('plugin \'%s\' unloaded' % p)
    
    def do_version(self, line):
        '''
        display pyraxshell version
        '''
        import version
        logging.info('pyraxshell version: %s' % version.VERSION)

    def get_names(self):
        '''
        override default method to auto-complete plug-ins names
        '''
        # get names from super method
        names = cmd.Cmd.get_names(self)
        # and append commands provided by plug-ins
        for p in self.plugin_names:
            names.append('do_' + p)
        return names
        
    def load_plugins(self):
        '''
        load plug-ins from './plugins' directory
        
        every plug-in filename is 'plugin_*.py'
        '''
        logging.debug('searching plug-ins')
        this_dir, this_filename = os.path.split(__file__)  # @UnusedVariable
        plugin_dir = os.path.join(os.path.abspath(this_dir), 'plugins')
        if not os.path.isdir(plugin_dir):
            logging.warn('plug-in directory \'%s\' is missing' % plugin_dir)
            return False
        files = os.listdir(plugin_dir)
        msg_loaded_plugins = '' 
        for f in files:
            if f[0:7] == 'plugin_' and f[-3:] == '.py':
                plugin_filename = os.path.join(plugin_dir, f)
                plugin = "%s%s" % ("plugins.", f[:-3])
                plugin_name = f[7:-3]
                logging.debug('plugin_filename: %s' % plugin_filename)
                logging.debug('plugin: %s' % plugin)
                logging.debug('plugin_name: \'%s\'' % plugin_name)
                __import__(plugin, globals(), locals(),
                           [('Cmd_%s' % plugin_name)], -1)
                self.plugin_names.append(plugin_name)
                p = imp.load_source(plugin, plugin_filename)
                p.injectme(self)
                msg_loaded_plugins += " " + plugin_name
        logging.debug('loading plug-ins done')
        logging.debug('plug-ins loaded: %s' %
                     ", ".join(sorted(msg_loaded_plugins.split())))
        return True

    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        # AUTHENTICATION
        import plugins.libauth
        pyrax_default_config_file = os.path.expanduser('~/.pyrax.cfg')
        if self.cfg.username != None and self.cfg.api_key != None:
# TODO --
            logging.debug("authenticating with login username:%s, apikey:%s" %
                          (self.cfg.username, self.cfg.api_key))
            try:
                (plugins.libauth.LibAuth().authenticate_login
                 (self.cfg.identity_type, self.cfg.username,
                  self.cfg.api_key, self.cfg.region))
            except:
                logging.warn('cannot login with %s' %
                             pyrax_default_config_file)
            logging.debug('authenticated as \'%s@%s\' in \'%s\'' %
                         (self.cfg.username, self.cfg.identity_type,
                          self.cfg.region))
        # try to authenticate automatically if '~/.pyrax.cfg' exists
        elif os.path.isfile(pyrax_default_config_file):
            try:
                plugins.libauth.LibAuth().authenticate_credentials_file(pyrax_default_config_file)
            except:
                logging.warn('cannot authenticate automatically with %s' %
                             pyrax_default_config_file)
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
        else:
            logging.debug('authenticated successfully')
