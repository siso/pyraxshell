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

    def get_group(self, id_or_name):
        '''
        look for scaling group with that id or name
        
        @param id_or_name    scaling group id or name
        @return              scaling group or None
        '''
        # look for a scaling group with that id
        try:
            sg = self.au.get(id_or_name)
            return sg
        except:
            msg = 'no group with id \'%s\'' % id_or_name
            self.r(0, msg, DEBUG)
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            # look for a scaling group with that name
            try:
                l_sg = self.au.list()
                for sg in l_sg:
                    if sg.name == id_or_name:
                        return sg
                # not an id not a name
                return None
            except:
                msg = 'no group with name \'%s\'' % id_or_name
                self.r(0, msg, DEBUG) 
                tb = traceback.format_exc()
                self.r(0, tb, DEBUG)
                return None

    def get_policy(self, group, id_or_name):
        '''
        look for scaling policy with that id or name
        
        @param group         scaling group
        @param id_or_name    scaling policy id or name
        @return              scaling policy or None
        '''
        # look for a scaling policy with that id
        try:
            sp = group.get_policy(id_or_name)
            return sp
        except:
            msg = 'no policy with id \'%s\'' % id_or_name
            self.r(0, msg, DEBUG)
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            # look for a scaling policy with that name
            try:
                l_sp = group.list_policies()
                for sp in l_sp:
                    if sp.name == id_or_name:
                        return sp
                # not an id not a name
                return None
            except:
                msg = 'no policy with name \'%s\'' % id_or_name
                self.r(0, msg, DEBUG) 
                tb = traceback.format_exc()
                self.r(0, tb, DEBUG)

    def get_webhook(self, policy, id_or_name):
        '''
        look for scaling policy with that id or name
        
        @param policy        scaling policy
        @param id_or_name    webhook id or name
        @return              scaling policy or None
        '''
        # look for a scaling group with that id
        try:
            return policy.get_webhook(id_or_name)
        except:
            msg = 'no webhook with id \'%s\'' % id_or_name
            self.r(0, msg, DEBUG)
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            # look for a webhook with that name
            try:
                lo_wh = policy.list_webhooks()
                for wh in lo_wh:
                    if wh.name == id_or_name:
                        return wh
                # not an id not a name
                return None
            except:
                msg = 'no policy with name \'%s\'' % id_or_name
                self.r(0, msg, DEBUG) 
                tb = traceback.format_exc()
                self.r(0, tb, DEBUG)

    def get_webhook_url(self, wh, rel='capability'):
        '''
        return webhook URL
        
        @param wh    webhook
        @param rel   'self' or 'capability'
        @return URL
        '''
        try:
            for i in wh.links:
                if i['rel'] == rel:
                    return i['href']
            return None
        except:
            tb = traceback.format_exc()
            self.r(0, tb, DEBUG)
            return None

    def list_webhooks(self, group, policy):
        '''
        list webhooks
        
        @param group         scaling group id
        @param policy        scaling policy id
        @return              webhooks list or None
        '''
        try:
            sg = self.get_group(group)
            if type(sg) is None:
                msg = 'no scaling group with id \'%s\'' % group
                self.r(0, msg, WARN)
                return False
            sp = self.get_policy(sg, policy)
            if type(sg) is None:
                msg = ('no scaling policy with id \'%s\'' % policy) 
                self.r(0, msg, WARN)
                return False
            return sp.list_webhooks()
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
