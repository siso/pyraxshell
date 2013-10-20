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

from globals import HOME_DIR
from globals import VERSION_FILE

VERSION='0.2.5'

def create_version_file():
    '''
    create version file in home directory
    '''
    with open(VERSION_FILE, 'w') as f:
        f.write(VERSION)

def read_version_file():
    '''
    read and return version from version file
    '''
    with open(VERSION_FILE, 'r') as f:
        version_on_disk = f.readline()
    if version_on_disk[-1] == '\n':
            version_on_disk = version_on_disk[:-1]
    return version_on_disk

def check_version_file():
    '''
    check if version file exists
    '''
    # is version file present?
    if not os.path.isfile(VERSION_FILE):
        # assuming VERSION_FILE is missing means fresh pyrashell installation
        create_version_file()
    # read version in version file
    version_on_disk = read_version_file()
    if not VERSION == version_on_disk:
        errmsg = ("Version mismatch. This is version '%s', but found version "
                  "'%s' in '%s'" % (VERSION, version_on_disk, HOME_DIR))
        errmsg += ("\nPlease, rename '%s' (i.e.: '%s.bak')" % (HOME_DIR,
                                                               HOME_DIR))
        logging.error(errmsg)
        return False
    return True
