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
import pyrax
import os.path
from prettytable import PrettyTable
from libpyraxshell import Libpyraxshell
import pprint

class LibAuth(object):
    '''
    pyraxshell authenticate library
    '''
    
    # ########################################
    # AUTHENTICATE
    
    def authenticate_credentials_file(self, credentials_file=None):
        '''authenticate with Rackspace Cloud
        
        using credentials file'''
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
                    logging.info("found credentials file: %s" % f)
                    break
                else:
                    logging.info("cannot find credentials file: %s" %
                                 os.path.expanduser(f))
            if self.credentials_file == None:
                logging.warn('cannot find pyrax config file '
                             '(default locations: \'%s\')'
                             % file_locations)
                return False
        try:
            pyrax.set_credential_file(self.credentials_file)
            return self.is_authenticated()
        except pyrax.exceptions.AuthenticationFailed:
            logging.warn('authentication failed: wrong credentials')
            logging.warning('failed authenticating with credentials file')
            return False
        except pyrax.exceptions.IdentityClassNotDefined:
            logging.warn('authentication failed: IdentityClassNotDefined. '
                         'Please, check credentials file')
            logging.warning('failed authenticating with credentials file')
            return False
        except Exception as e:
            logging.error('%s' % pprint.pprint(e))
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
            return self.is_authenticated()
        except pyrax.exceptions.AuthenticationFailed:
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
        pyrax.auth_with_token(token, tenantId, region=region)
    
    def is_authenticated(self):
        '''whether or not the user is authenticated'''
        try:
            return pyrax.identity.authenticated
        except Exception as inst:
            logging.debug('authentication test failed, not authenticated')
            tb = traceback.format_exc()
            logging.error(tb)
            return False
    
    def get_token(self):
        '''return the token issued by Rackspace Cloud'''
        return pyrax.identity.auth_token

    def print_pt_identity_info(self):
        '''
        print identity information of current authenticated user
        '''
        if self.is_authenticated():
            pt = PrettyTable(['key', 'value'])
            pt.add_row(['auth token', pyrax.identity.auth_token])
            pt.add_row(['authenticated', pyrax.identity.authenticated])
            pt.add_row(['region', pyrax.identity.region])
            pt.add_row(['regions', ','.join(r for r in pyrax.identity.regions)])
            pt.add_row(['tenant id', pyrax.identity.tenant_id])
            pt.add_row(['tenant name', pyrax.identity.tenant_name])
            pt.add_row(['username', pyrax.identity.username])
            pt.align['key'] = 'l'
            pt.align['value'] = 'l'
            pt.get_string(sortby='key')
            print pt
        else:
            logging.warn('cannot print identity information, authenticate first')
    
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
            return pyrax.identity.region
        except:
            logging.warn('unable to fetch region, are you authenticated?')
            return None
    
    # ########################################
    # VARIA
    def set_output_verbosity(self, value):
        '''
        debug HTTP activiti: True, False
        '''
        try:
            pyrax.set_http_debug(value)
        except:
            logging.warn('cannot set_output_verbosity(%s)' % value)
