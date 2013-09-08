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
import pyrax
import pprint

class Configuration(object):
    def __init__(self):
        # DEFAULTS
#         self.default_data_center = pyrax.default_region
        self.__default_identity_type = 'rackspace'
        self.__default_region = 'LON'
        self.__default_verbose = False
     
    def parsecli(self, cliargv):
        parser = argparse.ArgumentParser()
#         parser.add_argument("command", type=str,
#                             help="command to execute")
        parser.add_argument('-c', '--credentials',
                            help='file with credentials')
        parser.add_argument('-k', '--api-key', help='Authentication api-key')
        parser.add_argument('-i', '--identity-type',
                            help='identity type (default: \'rackspace\'')
        parser.add_argument('--pyrax-http-debug',
                            help = 'set pyrax http debug mode on',
                            action = 'store_true')
        parser.add_argument('-r', '--region', required=False,
                            help=('cloud data center to build the servers in'
                                  ' (default: %s)' % self.__default_region),
                            choices=['DFW', 'ORD', 'LON', 'SYD'],
                            default=pyrax.default_region)
        parser.add_argument('-u', '--username', help='Authentication username')
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="increase output verbosity")
        self.args = parser.parse_args()
        logging.debug('username: %s', self.args.username)
        # CHECK DEFAULTS
        if self.args.identity_type == None or self.args.identity_type == '':
            self.args.identity_type = self.__default_identity_type
        if self.args.region == None or self.args.region == '':
            self.args.region = self.__default_region
        if self.args.verbose != None or self.args.verbose == '':
            self.args.verbose = self.__default_verbose
        if self.args.pyrax_http_debug == None:
            self.args.pyrax_http_debug = False

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
    
    # --pyrax-http-debug (True)
    @property
    def pyrax_http_debug(self):
        return self.args.pyrax_http_debug
    
    # -r, --region
    @property
    def region(self):
        return self.args.region
    
    # -u, --username
    @property
    def username(self):
        return self.args.username
    
    # -v, --verbose
    @property
    def verbosity(self):
        return self.args.verbosity
     
    def __str__(self):
        return pprint.pformat(self.args)
