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
import importlib
import logging  # @UnusedImport
import os.path  # @UnusedImport

from plugins.plugin import Plugin
from utility import *  # @UnusedWildImport


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
        self.search_plugins()
        # cmd as singleton
        self.cfg = Configuration.Instance()  # @UndefinedVariable

        # no 'Cmd' output in non-interactive mode
        interactive = os.isatty(0)
        if not interactive:
            f = open(os.devnull, 'w')
            sys.stdout = f
        # list of methods to hide
        self.hidden_methods = ['EOF', 'plugin']

    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        terminate_threads()
        print
        sys.exit(0)

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
        msg = '''
pyraxshell - Copyright (c) 2013, Simone Soldateschi - All rights reserved.

author:   Simone Soldateschi
email:    simone.soldateschi@gmail.com
homepage: https://github.com/siso/pyraxshell
license:  GPLv3 or later (see LICENSE)'''
        self.r(0, msg, INFO)

    def do_license(self, line):
        '''
        display pyraxshell license
        '''
        msg = '''
pyraxshell is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyraxshell is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyraxshell. If not, see <http://www.gnu.org/licenses/>.'''
        self.r(0, msg, INFO)

    def do_list_plugins(self, line):
        '''
        list loaded plugins
        '''
        l = sorted(self.plugin_names)
        msg = "loaded plugins: %s" % ', '.join([p for p in l])
        self.r(0, msg, INFO)

    def do_log_level(self, line):
        '''
        set log level
        '''
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.arg.upper() in log_levels:
            l = logging.getLogger()
            for h in l.handlers:
                h.setLevel(self.arg.upper())
        else:
            cmd_out = 'log level can only be: %s' % ', '.join([l for l in
                                                               log_levels])
            self.r(0, cmd_out, WARN)

    def complete_log_level(self, text, line, begidx, endidx):
        params = ['debug', 'info', 'warning', 'error', 'critical']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_plugin(self, line):
        '''
        run PLUGIN.cmdloop()
        '''
        cmd, arg, line = self.parseline(line)  # @UnusedVariable
        if not cmd == '' and not cmd == None:
            i = importlib.import_module('pyraxshell.plugins.plugin_%s' % cmd)
            i.Plugin().cmdloop()

    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.
        """
        cmd, arg, line = self.parseline(line)  # @UnusedVariable
        if cmd in self.plugin_names:
            # change 'line' to make 'self.onecmd' call the right plugin
            # via 'do_plugin'
            line = "plugin %s" % cmd
        return line

    def do_version(self, line):
        '''
        display pyraxshell version
        '''
        import version
        msg = 'pyraxshell version: %s' % version.VERSION
        self.r(0, msg, INFO)

    def get_names(self):
        '''
        override default method to auto-complete plug-ins names
        '''
        # get names from super method
        names = cmd.Cmd.get_names(self)
        # remove methods to hide
        [names.remove('do_%s' % n) for n in self.hidden_methods]
        # and append commands provided by plug-ins
        for p in self.plugin_names:
            names.append('do_' + p)
        return names

    def do_scan_plugins(self, line):
        '''
        search plug-ins
        '''
        self.plugin_names = []
        self.search_plugins()

    def search_plugins(self):
        '''
        search plug-ins from './plugins' directory

        Every plug-in filename is in the form 'plugin_*.py'.
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
#                 __import__(plugin, globals(), locals(),
#                            [('Cmd_%s' % plugin_name)], -1)
                self.plugin_names.append(plugin_name)
#                 p = imp.load_source(plugin, plugin_filename)
#                 p.injectme(self)
                msg_loaded_plugins += " " + plugin_name
        logging.debug('seaching plug-ins done')
        logging.debug('plug-ins found: %s' %
                     ", ".join(sorted(msg_loaded_plugins.split())))
        return True

    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        # AUTHENTICATION
        import plugins.libauth
        pyrax_default_config_file = os.path.expanduser('~/.pyrax.cfg')
        if self.cfg.username != None and self.cfg.api_key != None:
            # authenticating with login
            logging.debug("authenticating with login username:%s, apikey:%s" %
                          (self.cfg.username, self.cfg.api_key))
            try:
                (plugins.libauth.LibAuth().authenticate_login
                 (self.cfg.identity_type, self.cfg.username,
                  self.cfg.api_key, self.cfg.region))
            except:
                cmd_out = 'cannot login with %s' % pyrax_default_config_file
                self.r(1, cmd_out, ERROR)
            logging.debug('authenticated as \'%s@%s\' in \'%s\'' %
                         (self.cfg.username, self.cfg.identity_type,
                          self.cfg.region))
        elif self.cfg.token != None:
            # authenticating with token
            logging.debug("authenticating with token:%s" % self.cfg.token)
            try:
                (plugins.libauth.LibAuth().authenticate_token
                 (self.cfg.token, self.cfg.tenant_id, self.cfg.region,
                  self.cfg.identity_type))
            except:
                tb = traceback.format_exc()
                self.r(1, tb, ERROR)
        elif os.path.isfile(pyrax_default_config_file):
            # try to authenticate automatically if '~/.pyrax.cfg' exists
            try:
                (plugins.libauth.LibAuth().
                 authenticate_credentials_file(pyrax_default_config_file))
            except:
                logging.warn('cannot authenticate automatically with %s' %
                             pyrax_default_config_file)
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
        else:
            logging.debug('authenticated successfully')
