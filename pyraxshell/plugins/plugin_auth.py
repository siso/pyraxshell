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
import traceback

from globals import ERROR, INFO
from plugins.libauth import LibAuth
from plugins.plugin import Plugin
import os.path

name = 'auth'

def injectme(c):
    setattr(c, 'do_auth', do_auth)
    logging.debug('%s injected' % __file__)

def do_auth(*args):
    Cmd_auth().cmdloop()


class Cmd_auth(Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Authenticate module
    '''
    
    prompt = "RS auth>"    # default prompt
    
    def __init__(self):
        Plugin.__init__(self)
        self.libplugin = LibAuth()

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

    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
    
    # ########################################
    # CLOUD AUTHENTICATION
    
#     def do_change_password(self, line):
#         '''
#         change user\'s password
#         '''
# #TODO --
#         logging.info('NOT IMPLEMENTED YET')
    
    def do_credentials(self, line):
        '''
        authentication with credentials file
        
        @param file    credential file (pyrax format)
        
        i.e.: credentials file:~/.pyrax
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name':'file', 'default':''}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        # additional checks
        _file = self.kvarg['file']
        if _file.find('~') == 0:
            _file = os.path.expanduser(_file)
        if _file != '' and not os.path.isfile(_file):
            cmd_out = 'cannot find file \'%s\'' % _file
            self.r(1, cmd_out, ERROR)
            return False
        # authenticating with credentials file
        if _file != None and _file != '':
            errcode = (self.libplugin.authenticate_credentials_file(_file))
        else:
            errcode = self.libplugin.authenticate_credentials_file()
        if errcode:
            cmd_out = "token: %s" % self.libplugin.get_token()
            self.r(0, cmd_out, INFO)
        else:
            cmd_out = ("cannot authenticate using credentials file")
            self.r(1, cmd_out, ERROR)
            return False
    
    def complete_credentials(self, text, line, begidx, endidx):
        params = ['file:']
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
    
    def do_is_authenticated(self, line):
        '''
        show Whether or not the user is authenticated
        '''
        retcode = 1
        if self.libplugin.is_authenticated():
            retcode = 0
        self.r(retcode, 'authenticated', INFO)
    
    def do_login(self, line):
        '''
        authenticate using username and api-key and authenticate
        
        Parameters:
        
        apikey
        username
        identity_type    (default: rackspace)
        region           (default: pyrax.default_region)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name':'apikey', 'required':True},
            {'name':'username', 'required':True},
            {'name':'identity_type', 'default':'rackspace'},
            {'name':'region', 'default':self.libplugin.default_region()}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        
        try:
            self.libplugin.authenticate_login(
                apikey = self.kvarg['apikey'],
                username = self.kvarg['username'],
                identity_type = self.kvarg['identity_type'],
                region = self.kvarg['region'],
            )
            cmd_out  = ('login - indentity_type:%s, username=%s, apikey=%s, '
                        'region=%s' % 
                        (self.kvarg['identity_type'], self.kvarg['username'],
                         self.kvarg['apikey'], self.kvarg['region']))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_login(self, text, line, begidx, endidx):
        params = ['identity_type:', 'username:', 'apikey:', 'region:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions

    def do_print_identity(self, line):
        '''
        print current identity information
        '''
        self.libplugin.print_pt_identity_info()
    
    def do_print_token(self, line):
        '''
        print token for current session
        '''
        if self.libplugin.is_authenticated():
            cmd_out = "token: %s" % self.libplugin.get_token()
            self.r(0, cmd_out, INFO)
    
    def do_token(self, line):
        '''
        authenticate using token and tenantId
        
        Parameters:
        
        identity_type    (default: rackspace)
        region           (default: LON)
        tenantId
        token
        '''
        retcode, retmsg = self.kvargcheck(
              {'name':'identity_type', 'default':'rackspace'},
              {'name':'region', 'default':'LON'},
              {'name':'tenantId', 'required':True},
              {'name':'token', 'required':True}
        )
        if not retcode:
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)
        try:
            self.libplugin.authenticate_token(
                identity_type=self.kvarg['identity_type'],
                region=self.kvarg['region'],
                tenantId=self.kvarg['tenantId'],
                token=self.kvarg['token'],
            )
            cmd_out = ('login - tenantId=%s, token=%s' %
                       (self.kvarg['tenantId'], self.kvarg['token']))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def complete_token(self, text, line, begidx, endidx):
        params = ['identity_type', 'region', 'tenantId', 'token']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
