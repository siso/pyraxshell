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

import logging
import os.path
import pprint
from prettytable import PrettyTable
import pyrax
import traceback

from account import Account
from globals import ERROR, INFO, WARN, DEBUG
from plugins.lib import Lib


class LibAuth(Lib):
    '''
    pyraxshell authenticate library
    '''
    
    # ########################################
    # ACCOUNTS FILE
    
    def get_account(self, stanza):
        '''
        return dictionary based on stanza alias from ACOUNTS_FILE
        '''
        out = {}
        a = Account.Instance()
        a.parse_config_file()
        out['identity_type'] = a.get_param(stanza, 'OS_AUTH_SYSTEM')
        out['username'] = a.get_param(stanza, 'OS_USERNAME')
        out['apikey'] = a.get_param(stanza, 'OS_PASSWORD')
        out['region'] = a.get_param(stanza, 'OS_REGION_NAME')
        return out
    
    def list_accounts(self):
        '''
        return a list of accounts defined in ACCOUNTS_FILE
        '''
        a = Account.Instance()
        a.parse_config_file()
        return a.list_stanzas()
    
    
    # ########################################
    # AUTHENTICATE
    
    def authenticate_credentials_file(self, credentials_file=None):
        '''
        authenticate with Rackspace Cloud
        
        @param credentials_file    credential file (pyrax format)
        @return    True if successful, False otherwise
        '''
        logging.debug('authenticating with credentials file \'%s\'' %
                      credentials_file)
        self.credentials_file = credentials_file
        if self.credentials_file == None:
            # search for credentials file default locations
            file_locations = ['~/.pyrax.cfg', './.pyrax.cfg']
            file_locations = [os.path.expanduser(f) for f in file_locations]
            for f in file_locations:
                if os.path.exists(os.path.expanduser(f)):
                    self.credentials_file = f
                    logging.debug("found credentials file: %s" % f)
                    break
                else:
                    logging.debug("cannot find credentials file: %s" %
                                 os.path.expanduser(f))
            if self.credentials_file == None:
                cmd_out = ('cannot find pyrax config file '
                           '(default locations: \'%s\')'
                           % file_locations)
                self.r(1, cmd_out, WARN)
                return False
        try:
            pyrax.set_credential_file(self.credentials_file)
            self.r(0, "authenticated", DEBUG)
            return self.is_authenticated()
        except pyrax.exceptions.AuthenticationFailed:
            cmd_out = 'authentication with credentials file failed'
            self.r(cmd_out)
            return False
        except pyrax.exceptions.IdentityClassNotDefined:
            cmd_out = ('authentication failed: IdentityClassNotDefined. '
                       'Please, check credentials file')
            self.r(1, cmd_out, WARN)
            return False
        except Exception as e:
            cmd_out = '%s' % pprint.pprint(e)
            self.r(1, cmd_out, WARN)
        return True
    
    def authenticate_login(self,
                           identity_type = "rackspace",
                           username = None,
                           apikey = None,
                           region = pyrax.default_region):
        '''authenticate with \'%s\'
        
        using username and api-key'''
        logging.debug('authenticating with login'
                      '(identity_type:%s, username:%s, api-key:%s, region=%s)'
                      % (identity_type, username, apikey, region))
        try:
            pyrax.set_setting("identity_type", identity_type)
            pyrax.set_credentials(username, apikey, region = region)
            cmd_out = "authentication with login successful"
            self.r(0, cmd_out, INFO)
            return self.is_authenticated()
        except pyrax.exceptions.AuthenticationFailed:
            cmd_out = "authentication with login failed"
            self.r(1, cmd_out, WARN)
            return False
    
    def authenticate_token(self, token, tenantId, region,
                           identity_type='rackspace'):
        '''authenticate with Rackspace Cloud
        
        using existing token
        
        tenantId: see top-right --> NAME (#XXX)
        '''
        logging.debug('setting identity_type=%s' % identity_type)
        pyrax.set_setting("identity_type", identity_type)
        logging.debug('authenticating with token:%s, tenantId:%s, region:%s ' %
                      (token, tenantId, region))
        try:
            pyrax.auth_with_token(token, tenantId, region=region)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def is_authenticated(self):
        '''whether or not the user is authenticated'''
        try:
            if pyrax.identity.authenticated:
                cmd_out = "user is authenticated"
                self.r(0, cmd_out, DEBUG)
                return True
            else:
                cmd_out = "user is not authenticated"
                self.r(0, cmd_out, DEBUG)
                return False
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False
    
    def get_token(self):
        '''return the token issued by Rackspace Cloud'''
        return pyrax.identity.auth_token

    def print_pt_identity_info(self):
        '''
        print identity information of current authenticated user
        '''
#TODO -- implement a function to build PrettyTable on the fly from JSON
#        interactively: print pt
#        non-interactively: print JSON
        if self.is_authenticated():
            pt = PrettyTable(['key', 'value'])
            pt.add_row(['auth token', pyrax.identity.auth_token])
            pt.add_row(['authenticated', pyrax.identity.authenticated])
            pt.add_row(['region', pyrax.identity.region])
            pt.add_row(['regions', ','.join(r for r in pyrax.identity.regions)])
            pt.add_row(['username', pyrax.identity.username])
            pt.add_row(['tenant id', pyrax.identity.tenant_id])
            pt.add_row(['tenant name', pyrax.identity.tenant_name])
            pt.align['key'] = 'l'
            pt.align['value'] = 'l'
            pt.get_string(sortby='key')
            print pt
        else:
            cmd_out = 'No info. Are you authenticated?'
            self.r(1, cmd_out, WARN)
    
    # ########################################
    # ENDPOINTS
    def list_endpoints(self):
        return pyrax.identity.services
    
    # ########################################
    # REGION
    def default_region(self):
        '''
        return default region defined in pyrax
        '''
        return pyrax.default_region
            
#     def default_region(self):
#         '''
#         return default region defined in pyrax
#         '''
#         return pyrax.default_region
    
    def get_region(self):
        '''
        return the region for which user is currently authenticated
        '''
        try:
            cmd_out = "region: %s" % pyrax.identity.region
            self.r(0, cmd_out, INFO)
            return pyrax.identity.region
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
    
    # ########################################
    # VARIA
    def set_output_verbosity(self, value):
        '''
        debug HTTP activiti: True, False
        '''
        try:
            pyrax.set_http_debug(value)
            cmd_out = "http_debu: %s" % value
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
