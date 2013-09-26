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

from db import DB
import logging
from configuration import Configuration
from utility import get_uuid
from singleton import Singleton

@Singleton
class Sessions(DB):
    '''
    manage sessions
    
    sid has a local meaning
    '''


    def __init__(self):
        '''
        Constructor
        '''
        DB.__init__(self)
        self.cfg = Configuration.Instance()  # @UndefinedVariable
        self.sid = get_uuid()
        logging.debug('session uuid:%s' % self.sid)

    def start_session(self):
        api_key = ''
        if hasattr(self.cfg, 'api_key') and self.cfg.api_key != None:
            api_key = self.cfg.api_key
        identity_type = ''
        if (hasattr(self.cfg, 'identity_type') and
            self.cfg.identity_type != None):
            identity_type = self.cfg.identity_type
        region = ''
        if hasattr(self.cfg, 'region') and self.cfg.region != None:
            region = self.cfg.region
        token = ''
        if hasattr(self.cfg, 'token') and self.cfg.token != None:
            token = self.cfg.token
        username = ''
        if hasattr(self.cfg, 'username') and self.cfg.username != None:
            username = self.cfg.username
        sql = ('''insert into sessions
        (sid, username, apikey, token, region,identity_type)
        values ('%s', '%s', '%s', '%s', '%s', '%s')''' %
        (self.sid, username, api_key, token, region, identity_type))
        logging.debug(sql)
        self.query(sql)

    def create_table_commands(self):
        '''
        create 'commands' table
        '''
        sql = '''
CREATE TABLE commands (
id    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
sid   TEXT,
t     timestamp default (strftime('%s', 'now')),
cmd_in    TEXT NOT NULL,
cmd_out   TEXT NOT NULL,
FOREIGN KEY(sid) REFERENCES sessions(id)
);
'''
        logging.debug(sql)
        self.query(sql)
        
    def create_table_sessions(self):
        '''
        create 'sessions' table
        '''
        sql = '''
CREATE TABLE sessions (
sid            TEXT PRIMARY KEY NOT NULL,
t              timestamp default (strftime('%s', 'now')),
username       TEXT NOT NULL,
apikey         TEXT NOT NULL,
token          TEXT NOT NULL,
region         TEXT NOT NULL,
identity_type  TEXT NOT NULL
);
'''
        logging.debug(sql)
        self.query(sql)

    def insert_table_commands(self, cmd_in, cmd_out):
        '''
        inster record in to 'commands' table
        '''
        logging.debug('cmd_in:%s, cmd_out:%s' % (cmd_in, cmd_out))
        sql = '''
INSERT INTO commands (sid, cmd_in, cmd_out)
VALUES ('%s', '%s', '%s')''' % (self.sid, cmd_in, cmd_out)
        logging.debug('sql: \'%s\'' % sql)
        self.query(sql)
