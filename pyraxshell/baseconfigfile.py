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

import ConfigParser
from globals import BASE_DIR


class BaseConfigFile:
    '''
    This base class is derived to implement classes based on key-value config
    file.
    '''

    def __init__(self, _file=None):
        '''
        Constructor set logger up, checks if config file exists, create it if
        needed, eventually parse it.
        '''
        self.logger = logging.getLogger(__name__)
        self._file = _file or os.path.join(BASE_DIR, 'sample.conf')
        self.check_config_file()
        self.parse_config_file()

    # ########################################
    # CONFIGURATION FILE

    def parse_config_file(self):
        '''
        parse configuration file
        '''
        self.check_config_file()
        self.config = ConfigParser.ConfigParser()
        self.config.read(self._file)

    def get_param(self, section, param, raw=1):
        """
        fetch a parameter from configuration file
        """
        return self.config.get(section, param, raw)

    def check_config_file(self):
        '''
        search config file, write it if missing
        '''
        if not os.path.isfile(self._file):
            self.logger.debug('creating default config file \'%s\'' %
                              self._file)
            cfg = '''[sample]
key = value
'''
            with open(self._file, 'w') as f:
                f.write(cfg)
                f.flush()
        else:
            self.logger.debug('found default config file \'%s\'' % self._file)

    def list_stanzas(self):
        '''
        return list of stanza in configuration file
        '''
        return self.config.sections()
