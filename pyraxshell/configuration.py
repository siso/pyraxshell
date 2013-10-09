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

import argparse
import logging
import os.path

from singleton import Singleton
import ConfigParser
from globals import CONFIG_FILE


@Singleton
class Configuration:
    '''
    CLI params and configuration file settings
    
    Configuration file settings are read first, and can be overwritten by
    CLI params.
    '''
    
    def __init__(self):
        # check if it is running interactively
        self.interactive = os.isatty(0)
        self.check_config_file()
    
    # ########################################
    # CONFIGURATION FILE
    
    def parse_config_file(self):
        '''
        parse configuration file
        '''
        self.check_config_file()
        self.config = ConfigParser.ConfigParser()
        self.config.read(CONFIG_FILE)
        
    def get_param(self, section, param, raw=1):
        """
        fetch a parameter from configuration file
        """
        return self.config.get(section, param, raw)
    
    def check_config_file(self):
        '''
        search config file, write it if missing
        '''
        config_file = CONFIG_FILE
        if not os.path.isfile(config_file):
            logging.debug('creating default config file \'%s\'' % config_file)
            cfg = '''[main]
verbose = false

[pyrax]
http_debug = False
no_verify_ssl = False
'''
            with open(config_file, 'w') as f:
                f.write(cfg)
                f.flush()
        else:
            logging.debug('found default config file \'%s\'' % config_file)


    # ########################################
    # CLI
    
    def parse_cli(self, cliargv):
        '''
        parse CLI parameters
        '''
        parser = argparse.ArgumentParser()
#         parser.add_argument("command", type=str,
#                             help="command to execute")
        parser.add_argument('-c', '--credentials',
                            help='file with credentials')
        parser.add_argument('-k', '--api-key', help='Authentication api-key')
        parser.add_argument('-i', '--identity-type',
                            help='identity type (default: \'rackspace\'',
                            default='rackspace')
        parser.add_argument('--pyrax-http-debug', nargs='?', const=True,
                            type=bool,
                            help = 'set pyrax http_debug on (default: False)')
        parser.add_argument('--pyrax-no-verify-ssl', nargs='?', const=True,
                            help = 'set pyrax verify_ssl (default: False)')
        parser.add_argument('-r', '--region', required=False,
                            help=('cloud data center to build the servers in'
                                  ' (default: LON)'),
                            choices=['DFW', 'ORD', 'LON', 'SYD'],
#                             default=pyrax.default_region
                            default='LON')
        parser.add_argument('--tenant-id', help='Authentication tenant id')
        parser.add_argument('-t', '--token', help='Authentication token')
        parser.add_argument('-u', '--username', help='Authentication username')
        parser.add_argument("-v", "--verbose", nargs='?', const=True,
                            help="verbose output (default: False)")
        self.args = parser.parse_args()

    
    # ########################################
    # SETTERs & GETTERs
        
    # -c
    @property
    def credentials(self):
        return self.args.credentials
    
    # -k, --api-key
    @property
    def api_key(self):
        return self.args.api_key
    
    # -i --identity-type
    @property
    def identity_type(self):
        return self.args.identity_type
    
    @property
    def interactive(self):
        return self.interactive

    # --pyrax-http-debug (True)
    @property
    def pyrax_http_debug(self):
        if self.args.pyrax_http_debug != None:
            return self.args.pyrax_http_debug
        else:
            return self.get_param('pyrax', 'http_debug')
    
    # --pyrax-no-verify-ssl
    @property
    def pyrax_no_verify_ssl(self):
        if self.args.pyrax_no_verify_ssl != None:
            return self.args.pyrax_no_verify_ssl
        else:
            return self.get_param('pyrax', 'no_verify_ssl')
    
    # -r, --region
    @property
    def region(self):
        return self.args.region
    
    # --tenant-id
    @property
    def tenant_id(self):
        return self.args.tenant_id
    
    # -t, --token
    @property
    def token(self):
        return self.args.token
    
    # -u, --username
    @property
    def username(self):
        return self.args.username
    
    # -v, --verbose
    @property
    def verbose(self):
        if self.args.verbose != None:
            return self.args.verbose
        else:
            return self.get_param('main', 'verbose')
     
    def __str__(self):
        '''
        string representation of Configuration
        '''
        return ("%s" %
                (', '.join( [ 'credentials:%s' % self.credentials,
                             'api-key:%s' % self.api_key,
                             'identity-type:%s' % self.identity_type,
                             'interactive:%s' % self.interactive,
                             'identity-type:%s' % self.identity_type,
                             'pyrax-http-debug:%s' % self.pyrax_http_debug,
                             'pyrax_no_verify_ssl:%s' % self.pyrax_no_verify_ssl,
                             'region:%s' % self.region,
                             'token:%s' % self.token,
                             'username:%s' % self.username,
                             'verbose:%s' % self.verbose,
                             ])))
