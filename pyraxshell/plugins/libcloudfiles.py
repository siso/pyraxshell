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

import pyrax
import traceback

from pyraxshell.globals import ERROR  # @UnresolvedImport
from pyraxshell.plugins.lib import Lib  # @UnresolvedImport


class LibCloudfiles(Lib):
    '''
    pyraxshell CloudFiles library
    '''

    def __init__(self):
        '''
        default constructor
        '''
        self.cf = pyrax.cloudfiles


#     def pt_containers_info(self):
#         '''
#         return PrettyTable with containers information
#         '''
#         try:
#             cc = self.cf.get_all_containers()
#             header = list_obj_properties(cc[0], pvt = False)
#             print '\n'.join(['%s' % c.name for c in cc])
#         except:
#             self.r(1, traceback.format_exc(), ERROR)
#             return False
