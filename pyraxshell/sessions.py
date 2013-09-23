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

class Sessions(DB):
    '''
    manage sessions
    '''


    def __init__(self):
        '''
        Constructor
        '''
        DB.__init__(self)

    def create_table_commands(self):
        sql = '''
CREATE TABLE commands (
id    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
sid   INTEGER,
t     timestamp default (strftime('%s', 'now')),
cmd_in    TEXT NOT NULL,
cmd_out   TEXT NOT NULL,
FOREIGN KEY(sid) REFERENCES sessions(id)
);
'''
        logging.debug(sql)
        self.query(sql)
        
    def create_table_sessions(self):
        sql = '''
CREATE TABLE sessions (
id             INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
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
