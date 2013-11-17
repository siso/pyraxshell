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

import traceback

from pyraxshell.globals import ERROR, INFO, WARN, DEBUG
from pyraxshell.plugins.libautoscale import LibAutoscale
import pyraxshell.plugins.plugin
from pyraxshell.utility import objects_to_pretty_table
from pyraxshell.utility import kv_dict_to_pretty_table


class Plugin(pyraxshell.plugins.plugin.Plugin):
    '''
    pyrax shell POC - Autoscale module
    '''

    prompt = "RS autoscale>"    # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
        self.libplugin = LibAutoscale()
        self.au = self.libplugin.au
    
    def cmdloop(self):
        # check if 'autoscale' feature is available for the account
        if self.au is None:
            msg = 'autoscale feature not available'
            self.r(0, msg, WARN)
            return False
        return pyraxshell.plugins.plugin.Plugin.cmdloop(self)
    
    def complete_id(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions
    
    def do_info(self, line):
        '''
        display scaling group info
        
        id    scaling group id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
#         self.r(0, retmsg, INFO)  # everything's ok
        sg = None
        try:
            sg = self.au.get(self.kvarg['id'])
        except:
            msg = 'cannot find scaling group with id:%s' % self.kvarg['id']
            self.r(0, msg, WARN)
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            return False
        # build key-value dict to print
        try:
            msg = ''
            try:
                msg = '## Configuration\n'
                pt = kv_dict_to_pretty_table(sg.get_configuration())
                pt.align['value'] = 'l'
                msg += str(pt)
            except: 
                self.r(0, 'cannot fetch configuration', WARN)
            try:
                msg += '\n\n## State\n'
                pt = kv_dict_to_pretty_table(sg.get_state())
                pt.align['value'] = 'l'
                msg += str(pt)
            except:
                self.r(0, 'cannot fetch state', WARN)
            #
            self.r(0, msg, INFO)
        except:
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            return False
    
    def complete_info(self, text, line, begidx, endidx):
        return self.complete_id(text, line, begidx, endidx)

    def do_list(self, line):
        '''
        list Scaling Groups
        '''
        sg = self.au.list()
        # properties to be displayed
        props = ['id', 'name', 'cooldown', 'min_entities', 'max_entities',
                 'metadata']
        # create a PrettyTable obj with those columns
        pt = objects_to_pretty_table(sg, props)
        # PrettyTable style
        pt.align['name'] = 'l'
        for c in props[1:]:
            pt.align[c] = 'r'
        pt.sortby = 'name'
        #
#         print pt
        self.r(0, pt, INFO)

    def do_list_policies(self, line):
        '''
        list Scaling Groups
        id    scaling group id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        try:
            policies = self.au.list_policies(self.kvarg['id'])
            # properties to be displayed
            props = ['id', 'args', 'change', 'cooldown', 'name', 'type']
            # create a PrettyTable obj with those columns
            pt = objects_to_pretty_table(policies, props)
            # PrettyTable style
            pt.align['name'] = 'l'
            for c in props[1:]:
                pt.align[c] = 'r'
            pt.sortby = 'name'
            self.r(0, pt, INFO)
        except:
            msg = 'cannot find scaling group with id:%s' % self.kvarg['id']
            self.r(0, msg, WARN)
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            return False

    def complete_list_policies(self, text, line, begidx, endidx):
        return self.complete_id(text, line, begidx, endidx)
