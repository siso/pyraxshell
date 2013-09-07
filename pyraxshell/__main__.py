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

from libpyraxshell import Libpyraxshell

import cmd
import logging  # @UnusedImport
from configuration import Configuration
import sys
import utility
import os.path  # @UnusedImport
from utility import *  # @UnusedWildImport
import imp
import plugins  # @UnusedImport
import pprint
import pyrax


class RaxShell(cmd.Cmd):
    """
    pyrax shell POC
    """
    
    prompt = "H>"    # default prompt
    
    def __init__(self, cfg, libpyraxshell):
        cmd.Cmd.__init__(self)
        self.cfg = cfg
        self.libpyraxshell = libpyraxshell
        self.plugin_names = list()
        self.load_plugins()

    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True

    def do_endpoints(self, line):
        '''
        managing servers
        '''
        logging.debug("line: %s" % line)
        pprint.pprint(pyrax.identity.services)
    
    def do_exit(self,*args):
        return True
    
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
    
    def do_version(self, line):
        '''
        display pyraxshell version
        '''
        import version
        logging.info('pyraxshell version: %s' % version.version)

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
                self.plugin_names.append(plugin_name)
                p = imp.load_source(plugin, plugin_filename)
                p.injectme(self)
                msg_loaded_plugins += " " + plugin_name
        logging.debug('loading plug-ins done')
        logging.info('plug-ins loaded: %s' %
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
            logging.info('authenticated as \'%s@%s\' in \'%s\'' %
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
            logging.info('authenticated successfully')
        

def main():
    # ########################################
    # LOGGING
    utility.logging_start()  # @UndefinedVariable
    logging.debug('starting')
    
    # ########################################
    # CONFIGURATION
    cfg = Configuration()
    cfg.parsecli(sys.argv)
    logging.info("configuration: %s" % cfg)
    
    # ########################################
    # DO STUFF
    libpyraxshell = Libpyraxshell()
    raxshell = RaxShell(cfg, libpyraxshell)
    raxshell.cmdloop()

if __name__ == '__main__':
    main()
