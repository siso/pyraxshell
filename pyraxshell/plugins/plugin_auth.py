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
from plugins.libauth import LibAuth
from plugins.plugin import Plugin
from globals import INFO, ERROR
import traceback

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
        '''
# TODO -- accept path to file with credentials 
        logging.debug("authenticating with credentials file")
        if self.libplugin.authenticate_credentials_file():
            cmd_out = "token: %s" % self.libplugin.get_token()
            self.r(0, cmd_out, INFO)
        else:
            cmd_out = "cannot authenticate using pyrax credentials file"
            self.r(1, cmd_out, ERROR)

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
        
        identity_type = 'rackspace'    (default)
        username
        apikey
        region                         (default: pyrax.default_region)
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        _identity_type = 'rackspace'
        _username = None
        _apikey = None
        _region = self.libplugin.default_region()
        # parsing parameters
        if 'identity_type' in d_kv.keys():
            _identity_type = d_kv['identity_type']
        else:
            logging.debug("identity_type: %s (default)" % _identity_type)
        if 'username' in d_kv.keys():
            _username = d_kv['username']
        else:
            cmd_out = "missing username"
            self.r(1, cmd_out, ERROR)
            return False
        if 'apikey' in d_kv.keys():
            _apikey = d_kv['apikey']
        else:
            cmd_out = "missing apikey"
            self.r(1, cmd_out, ERROR)
            return False
        if 'region' in d_kv.keys():
            _region = d_kv['region']
        try:
            self.libplugin.authenticate_login(identity_type = _identity_type,
                                                  username = _username,
                                                  apikey = _apikey,
                                                  region = _region)
            cmd_out  = ('login - indentity_type:%s, username=%s, apikey=%s, '
                        'region=%s' %
                        (_identity_type, _username, _apikey, _region))
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
        
        identity_type
        region
        tenantId
        token
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        _identity_type = None
        _region = None
        _tenantId = None
        _token = None
        if 'identity_type' in d_kv.keys():
            _identity_type = d_kv['identity_type']
        else:
            cmd_out = "missing identity_type"
            self.r(1, cmd_out, ERROR)
            return False
        if 'region' in d_kv.keys():
            _region = d_kv['region']
        else:
            cmd_out = "missing region"
            self.r(1, cmd_out, ERROR)
            return False
        # parsing parameters
        if 'tenantId' in d_kv.keys():
            _tenantId = d_kv['tenantId']
        else:
            cmd_out = "missing tenantId"
            self.r(1, cmd_out, ERROR)
            return False
        if 'token' in d_kv.keys():
            _token = d_kv['token']
        else:
            cmd_out = "missing token"
            self.r(1, cmd_out, ERROR)
            return False
        #
        print "-" * 10
        print _tenantId, _token
        try:
            self.libplugin.authenticate_token(token=_token, tenantId=_tenantId,
                                              region=_region,
                                              identity_type=_identity_type)
            cmd_out = 'login - tenantId=%s, token=%s' % (_tenantId, _token)
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
