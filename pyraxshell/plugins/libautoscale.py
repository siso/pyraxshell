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

import keyring
import logging
import os.path
import pprint
from prettytable import PrettyTable
import pyrax
import traceback

from pyraxshell.account import Account
from pyraxshell.globals import ERROR, INFO, WARN, DEBUG
from pyraxshell.plugins.lib import Lib


class LibAutoscale(Lib):
    '''
    Autoscale library
    '''

    def __init__(self):
        self.au = pyrax.autoscale

    def is_ready(self):
        '''
        return the status of this capability
        '''
        print 'self.au: %s' % self.au
        if self.au is None:
            msg = 'cannot get autoscale object'
            self.r(0, msg, DEBUG)
            return (1, msg, ERROR)
        return (0, 'autoscale ready', INFO)
    
    
