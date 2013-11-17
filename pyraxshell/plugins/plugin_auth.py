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

import cmd
import os.path
import pyrax
import traceback

from pyraxshell.globals import ERROR, INFO, WARN, DEBUG
from pyraxshell.plugins.libauth import LibAuth
import pyraxshell.plugins.plugin


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Authenticate module
    '''

    prompt = "RS auth>"    # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
        self.libplugin = LibAuth()

    # ########################################
    # CLOUD AUTHENTICATION

#     def do_change_password(self, line):
#         '''
#         change user\'s password
#         '''
# #TODO --
#         logging.info('NOT IMPLEMENTED YET')

    def do_account(self, line):
        '''
        authenticate using ACCOUNT_FILE

        @param alias    account alias (i.e.: name of stanza in ACCOUNT_FILE)
        '''
        try:
            self.libplugin.authenticate_login(
                **self.libplugin.get_account(self.arg))
#                 identity_type = ,
#                 username = None,
#                 apikey = None,
#                 region = pyrax.default_region)
#             self.r(*self.libplugin.get_identity_info())
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_account(self, text, line, begidx, endidx):
        params = self.libplugin.list_accounts()
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_credentials(self, line):
        '''
        authentication with credentials file

        @param file    credential file (pyrax format)

        i.e.: credentials file:~/.pyrax
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'file', 'default': ''}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)     # everything's ok
        # additional checks
        _file = self.kvarg['file']
        if _file.find('~') == 0:
            _file = os.path.expanduser(_file)
        if _file != '' and not os.path.isfile(_file):
            cmd_out = 'cannot find file \'%s\'' % _file
            self.r(1, cmd_out, ERROR)
            return False
        # authenticating with credentials file
        if _file is not None and _file != '':
            errcode = (self.libplugin.authenticate_credentials_file(_file))
        else:
            errcode = self.libplugin.authenticate_credentials_file()
        if errcode:
            cmd_out = "token: %s" % self.libplugin.get_token()
            self.r(0, cmd_out, INFO)
        else:
            cmd_out = ("cannot authenticate using credentials file")
            self.r(1, cmd_out, ERROR)
            return False

    def complete_credentials(self, text, line, begidx, endidx):
        params = ['file:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_exit(self, *args):
        return True

    def do_is_authenticated(self, line):
        '''
        show Whether or not the user is authenticated
        '''
        self.r(0, self.libplugin.is_authenticated(), INFO)

    def do_list(self, line):
        '''
        list accounts defined in ACCOUNTS_FILE
        '''
        cmd_out = '\n'.join([a for a in self.libplugin.list_accounts()])
        self.r(0, cmd_out, INFO)

    def do_login(self, line):
        '''
        authenticate using username and api-key and authenticate

        Parameters:

        apikey
        username
        identity_type    (default: rackspace)
        region           (default: pyrax.default_region)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'apikey', 'required': True},
            {'name': 'username', 'required': True},
            {'name': 'identity_type', 'default': 'rackspace'},
            {'name': 'region', 'default': self.libplugin.default_region()}
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, DEBUG)     # everything's ok

        try:
            self.libplugin.authenticate_login(
                apikey=self.kvarg['apikey'],
                username=self.kvarg['username'],
                identity_type=self.kvarg['identity_type'],
                region=self.kvarg['region'],
            )
            self.r(*self.libplugin.get_identity_info())
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_login(self, text, line, begidx, endidx):
        params = ['identity_type:', 'username:', 'apikey:', 'region:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_print_identity(self, line):
        '''
        print current identity information
        '''
        self.r(0, self.libplugin.pt_identity_info(), INFO)

    def do_print_token(self, line):
        '''
        print token for current session
        '''
        if self.libplugin.is_authenticated():
            cmd_out = "token: %s" % self.libplugin.get_token()
            self.r(0, cmd_out, INFO)

    def do_token(self, line):
        '''
        authenticate using token and tenantId

        Parameters:

        identity_type    (default: rackspace)
        region           (default: LON)
        tenantId
        token
        '''
        retcode, retmsg = self.kvargcheck(
            {'name': 'identity_type', 'default': 'rackspace'},
            {'name': 'region', 'default': 'LON'},
            {'name': 'tenantId', 'required': True},
            {'name': 'token', 'required': True}
        )
        if not retcode:
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, DEBUG)
        try:
            self.libplugin.authenticate_token(
                identity_type=self.kvarg['identity_type'],
                region=self.kvarg['region'],
                tenantId=self.kvarg['tenantId'],
                token=self.kvarg['token'],
            )
            self.r(*self.libplugin.get_identity_info())
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_token(self, text, line, begidx, endidx):
        params = ['identity_type:', 'region:', 'tenantId:', 'token:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_whoami(self, line):
        '''
        print briefly current identity
        '''
        try:
            msg = ('username: %s, region: %s, identity_type: %s' %
                   (pyrax.identity.username, pyrax.identity.region,
                    pyrax.get_setting('identity_type')))
            self.r(0, msg, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
