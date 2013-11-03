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

import os.path

from baseconfigfile import BaseConfigFile
from globals import ACCOUNTS_FILE
from singleton import Singleton


@Singleton
class Account(BaseConfigFile):
    '''
    Account manager
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._file = ACCOUNTS_FILE
        BaseConfigFile.__init__(self, self._file)

    # ########################################
    # CONFIGURATION FILE

    def check_config_file(self):
        '''
        search config file, write it if missing
        '''
        if not os.path.isfile(self._file):
            self.logger.debug('creating default config file \'%s\'' %
                              self._file)
            cfg = '''#[account_alias_0]
#OS_USERNAME = foo
#OS_PASSWORD = a_very_secure_password
#OS_PASSWORD = USE_KEYRING
#OS_TENANT_NAME = "0123456789"
#OS_AUTH_URL = "https://identity.api.rackspacecloud.com/v2.0/"
#OS_COMPUTE_API_VERSION = 1.1
#OS_AUTH_SYSTEM = "rackspace"
#OS_REGION_NAME = HKG
#NOVA_SERVICE_NAME = cloudServersOpenStack
'''
            with open(self._file, 'w') as f:
                f.write(cfg)
                f.flush()
        else:
            self.logger.debug('found default config file \'%s\'' % self._file)