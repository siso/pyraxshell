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

import logging  # @UnusedImport
import logging.config
import os.path
import traceback

from globals import LOG_CONF_FILE


def check_config_file():
    '''
    search logging configuration file, write it if missing
    '''
    if not os.path.isfile(LOG_CONF_FILE):
        with open(LOG_CONF_FILE, 'w') as f:
            log_cfg = '''
[loggers]
keys=root

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,consoleFormatter

[logger_root]
level=DEBUG
handlers=fileHandler,consoleHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=consoleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=handlers.RotatingFileHandler
level=DEBUG
args=(os.path.expanduser('~/.pyraxshell/pyraxshell.log'),'a','maxBytes=1024k','backupCount=5')
formatter=simpleFormatter

[formatter_simpleFormatter]
format=%(asctime)s %(name)s %(levelname)s %(module)s %(message)s
datefmt=

[formatter_consoleFormatter]
format=%(message)s (%(levelname)s)
datefmt=
'''
            f.write(log_cfg)
            f.flush()


def start_logging():
    '''
    start logging facility, write default configuration file if missing
    '''
    check_config_file()
    try:
        this_dir, this_filename = os.path.split(__file__)  # @UnusedVariable
        log_config_file_locations = [LOG_CONF_FILE]
        log_config_file = None
        for f in log_config_file_locations:
            if os.path.exists(os.path.expanduser(f)):
                logging.debug("found log config file: %s" %
                              os.path.expanduser(f))
                log_config_file = os.path.expanduser(f)
                logging.config.fileConfig(log_config_file)
        if log_config_file == None:
            logging.warn('could not find log config file (default locations: '
                         '\'%s\')' % log_config_file_locations)
            return False
        return True
    except:
        print traceback.format_exc()
