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
import logging
from prettytable import PrettyTable
import pyrax
import traceback

from pyraxshell.globals import INFO, ERROR, WARNING, POLL_TIME
import pyraxshell.plugins.plugin
from pyraxshell.plugins.libservers import LibServers, ServerCreatorThread


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Manage servers module
    '''

    prompt = "RS servers>"  # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
        self.libplugin = LibServers()

    # ########################################
    # SERVER
    def do_change_password(self, line):
        '''
        reboot server

        id        server id
        password  new password
        '''
#         cmd_in = "%s %s" % (inspect.stack()[0][3][3:], line)
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'password', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            s = self.libplugin.get_by_id(self.kvarg['id'])
        except IndexError:
            cmd_out = 'server id:%s not found' % self.kvarg['id']
            self.r(1, cmd_out, WARNING)
            return False
        try:
            if s.status == 'ACTIVE':
                s.change_password(self.kvarg['password'])
                cmd_out = ('changed root password on server id:%s, name:%s' %
                           (self.kvarg['id'], s.name))
                self.r(0, cmd_out, INFO)
            else:
                cmd_out = ('cannot change root password on server id:%s, '
                           'name:%s' % (self.kvarg['id'], s.name))
                self.r(1, cmd_out, ERROR)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_change_password(self, text, line, begidx, endidx):
        params = ['id:', 'password:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_create(self, line):
        '''
        create a new server

        Parameters:

        flavor_id        see: list_flavors
        image_id         see: list_images
        name
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'flavor_id', 'required': True},
            {'name': 'image_id', 'required': True},
            {'name': 'name', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            # create ServerCreatorTread
            sct = ServerCreatorThread(self.kvarg['name'],
                                      self.kvarg['flavor_id'],
                                      self.kvarg['image_id'],
                                      poll_time=POLL_TIME)
            # start thread
            sct.setName('%s' % self.kvarg['name'])
            sct.start()
            # completion message printed by thread in libservers
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_create(self, text, line, begidx, endidx):
        params = ['flavor_id:', 'image_id:', 'name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
# TODO --
        last_token = line.split()[-1]
        logging.debug("last_token: %s" % last_token)
        if last_token == 'flavor_id:':
            logging.debug("auto-complete flavour")
        elif last_token == 'image_id:':
            logging.debug("auto-complete image_id")
        elif last_token == 'name:':
            logging.debug("auto-complete name")
        return completions

    def do_delete(self, line):
        '''
        delete server

        It is safer deleting a CloudServer by id, as different servers
        could have the same name.

        Parameters:
        id     server id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        self.libplugin.delete_server(self.kvarg['id'])
        cmd_out = 'deleting server id:%s' % self.kvarg['id']
        self.r(0, cmd_out, INFO)

    def complete_delete(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_details(self, line):
        '''
        display server details
        id or name must be specified

        Parameters:

        id        server id
        name      server name

        i.e.: H servers> details name:foo
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'name', 'default': ''}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            # output in libservers
            self.libplugin.details_server(self.kvarg['id'], self.kvarg['name'])
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False

    def complete_details(self, text, line, begidx, endidx):
        params = ['id:', 'name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_exit(self, *args):
        return True

    def do_flavors(self, line):
        '''
        list servers flavors
        '''
        print self.libplugin.pt_cloudservers()

    def do_list(self, line):
        '''
        list my servers
        '''
        msg = self.libplugin.print_pt_cloudservers()
        self.r(0, msg, INFO)

    def do_images(self, line):
        '''
        list servers images
        '''
        msg = self.libplugin.print_pt_cloudservers_images()
        self.r(0, msg, INFO)

    def do_reboot(self, line):
        '''
        reboot server

        id        server id to reboot
        type      'cold' or 'hard' reboot
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'type', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        _type = str.upper(self.kvarg['type'])
        if _type != 'COLD' and _type != 'HARD':
            cmd_out = "reboot type can be: cold or hard, not \'%s\'" % _type
            self.r(1, cmd_out, WARNING)
            return False
        try:
            s = self.libplugin.get_by_id(self.kvarg['id'])
            self.r(0, cmd_out, INFO)
        except IndexError:
            cmd_out = ('cannot find server identified with id:%s' %
                       self.kvarg['id'])
            self.r(1, cmd_out, ERROR)
            return False
        try:
            if s.status == 'ACTIVE':
                s.reboot(_type)
                cmd_out = ('%s rebooted server id:%s' % (_type,
                                                         self.kvarg['id']))
                self.r(0, cmd_out, INFO)
            else:
                cmd_out = ('cannot reboot server id:%s, status:%s' %
                           (self.kvarg['id'], s.status))
                self.r(1, cmd_out, ERROR)
                return False

        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def complete_reboot(self, text, line, begidx, endidx):
        params = ['id:', 'type:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    # ########################################
    # SERVER SNAPSHOTS
    #
    # "qui pro quo": server snapshots are called 'snapshot' when using API
    #                and 'images' on the web Control Panel, which might lead to
    #                confusion, as images are also called (on the web Control
    #                Panel and in the API) the 'initial images' to use to spin
    #                up servers
    def do_take_snapshots(self, line):
        '''
        create an image of a server

        id               server id
        snapshot_name    name of the snapshot to be taken
#TODO   metadata         key-value pairs metadata
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'id', 'required': True},
            {'name': 'snapshot_name', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            s = self.libplugin.get_by_id(self.kvarg['id'])
        except IndexError:
            cmd_out = ('cannot find server identified by id:%s' %
                       self.kvarg['id'])
            self.r(1, cmd_out, ERROR)
            return False
        try:
            s.create_image(self.kvarg['snapshot_name'])
            cmd_out = ('snapshot name:%s of server id:%s' %
                       (self.kvarg['snapshot_name'], self.kvarg['id']))
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None

    def complete_take_snapshots(self, text, line, begidx, endidx):
        params = ['id:', 'snapshot_name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_delete_snapshot(self, line):
        '''
        delete snapshot

        Parameters:
        id     snapshot id
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck({'name': 'id', 'required': True})
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            cs = pyrax.cloudservers
            snapshot = [ss for ss in cs.list_snapshots() if ss.id ==
                        self.kvarg['id']][0]
            snapshot.delete()
            cmd_out = 'deleted snapshot id:%s' % snapshot.id
            self.r(0, cmd_out, INFO)
        except IndexError:
            cmd_out = ('cannot find snapshot identified by id:%s' %
                       self.kvarg['id'])
            self.r(1, cmd_out, ERROR)
            return False
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None

    def complete_delete_snapshot(self, text, line, begidx, endidx):
        params = ['id:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_list_snapshots(self, line):
        '''
        list snapshots
        '''
        logging.info("list snapshots")
        logging.debug("line: %s" % line)
        try:
            cs = pyrax.cloudservers
            pt = PrettyTable(['id', 'name', 'created', 'minDisk', 'minRam',
                              'progress', 'server id', 'status', 'updated'])
            for ss in cs.list_snapshots():
                pt.add_row([
                                ss.id,
                                ss.name,
                                ss.created,
                                ss.minDisk,
                                ss.minRam,
                                ss.progress,
                                ss.server['id'],
                                ss.status,
                                ss.updated
                            ])
            pt.align['id'] = 'l'
            pt.align['name'] = 'l'
            self.r(0, str(pt), INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return None
