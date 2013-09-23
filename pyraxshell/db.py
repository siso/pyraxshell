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
from globals import SQLITE_DB
import os.path
import sqlite3


class DB:
    '''
    manage db
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.start_db()
    
    def __del__(self):
        '''
        Destructor
        '''
        self.close_db()
    
    def close_db(self):
        '''
        close db handles
        '''
        self.__con.commit()
        self.__con.close()
    
    def query(self, sql):
        '''
        query db
        '''
        logging.debug('sql:%s' % sql)
        cur = self.__con.cursor()
        cur.execute(sql)
        self.__con.commit()
        return cur.fetchall()

    def start_db(self):
        '''access db, create a new db if it is missing'''
        dbfilename = os.path.expanduser(SQLITE_DB)
        if not os.path.isfile(dbfilename):
            logging.info("db file '%s' is missing, creating it" % dbfilename)
            self.__con = sqlite3.connect(dbfilename)  # @UndefinedVariable
#             self.create_db_schema()
        else:
            logging.debug('database found (\'%s\')' % dbfilename)
            self.__con = sqlite3.connect(dbfilename)  # @UndefinedVariable