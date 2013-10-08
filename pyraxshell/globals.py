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

import os.path

import Queue


# home directory
HOME_DIR = os.path.expanduser('~/.pyraxshell')

# SQLite database, public ip addresses history
SQLITE_DB = os.path.expanduser('~/.pyraxshell/db.sqlite3')

# main configuration file
CONFIG_FILE = os.path.expanduser('~/.pyraxshell/pyraxshell.conf')

# logging configuration file
LOG_CONF_FILE = os.path.expanduser('~/.pyraxshell/logging.conf')

# log file
LOG_FILE = os.path.expanduser('~/.pyraxshell/pyraxshell.log')

# log levels
DEBUG = 0
INFO = INFORMATION = 1
WARN = WARNING = 2
ERROR = 3
CRITICAL = 4
log_levels = (DEBUG, INFO, WARN, ERROR, CRITICAL)


# message queue
msg_queue = Queue.Queue()

# polling time in seconds
POLL_TIME = 30
