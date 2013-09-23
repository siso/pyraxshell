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

import sys
import terminalsize
import os.path
import logging  # @UnusedImport
import logging.config
from globals import LOG_CONF_FILE, HOME_DIR, CONFIG_FILE
import db
import sessions
import traceback


def check_dir_home():
    '''
    check and create missing dirs and files
    '''
    if not os.path.isdir(os.path.expanduser(HOME_DIR)):
        # create dirs and config files
        check_dir(os.path.expanduser(HOME_DIR))
        create_default_conf()
        create_default_log_conf()
        #create db
        db.DB()
        sessions.Sessions().create_table_sessions()
        sessions.Sessions().create_table_commands()
        return False
    return True

def check_dir(directory):
    '''
    Check dir, create it if necessary
    '''
    if not os.path.isdir(directory):
        logging.info("ipnotify directory '%s' is missing, creating it" % directory)
        try:
            os.mkdir(directory)
        except OSError as exc:
            logging.warn("error creating directory '%s'")
            raise exc

def create_default_conf():
    '''
    write default configuration file
    '''
    cfg = '''
THIS IS FOR FUTURE USE
'''
    with open(os.path.expanduser(CONFIG_FILE), 'w') as f:
        f.write(cfg)
        f.flush()

def create_default_log_conf():
    '''
    write default logging configuration file
    '''
    log_cfg = '''[loggers]
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
format=%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s
datefmt=

[formatter_consoleFormatter]
format=%(message)s (%(levelname)s)
datefmt=
'''
    with open(os.path.expanduser(LOG_CONF_FILE), 'w') as f:
        f.write(log_cfg)
        f.flush()

def kvstring_to_dict(kvs):
    '''
    transform a key-value-string to dictionary
    key-value separator can be ':' or '=', even mixed!
    
    return None in case of error
    
    i.e.: "k0:v0 k1:v1 ... ki:vi" ==> {'k0':'v0','k1':'v1','ki':'vi'}
    '''
    logging.debug(kvs)
    d_out = {}
    kvs = kvs.replace('=', ':')
    try:
        for token in kvs.split():
            kv = token.split(':')
            d_out[kv[0]] = kv[1]
    except:
        logging.error('cannot parse key-value-string')
    return d_out

def logging_start():
    try:
        this_dir, this_filename = os.path.split(__file__)  # @UnusedVariable
        log_config_file_locations = [LOG_CONF_FILE]
        log_config_file = None    
        for f in log_config_file_locations:
            if os.path.exists(os.path.expanduser(f)):
                log_config_file = f
                logging.config.fileConfig(log_config_file)
                logging.debug("found log config file: %s" % f)
        if log_config_file == None:
            logging.warn('could not find log config file (default locations: \'%s\')'
                         % log_config_file_locations)
    except:
        print traceback.format_exc()

def is_ipv4(address):
    '''
    check if address is valid IP v4
    '''
    import socket
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False

def is_ipv6(address):
    '''
    check if address is valid IP v6
    '''
    import socket
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except socket.error:
        return False

def get_ip_family(address):
    '''
    obtain the address family an IP belongs to
    '''
    if is_ipv4(address):
        return 'ipv4'
    elif is_ipv6(address):
        return 'ipv6'
    return None

def print_dict(d, indent=0, indent_string="--"):
    '''recursively print nested dictionaries''' 
    for k, v in d.items():
        if type(v) is not dict:
            print "%s%s --> %s" % ((indent_string * indent), k, v)
        else:
            print "%s%s:" % ((indent_string * indent), k)
            print_dict(v, indent + 1)

def print_there(row, col, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (row, col, text))
    sys.stdout.flush()

def print_top_right(text):
    '''
    print text to top right in terminal
    '''
    (width, heigth) = terminalsize.get_terminal_size()  # @UnusedVariable
    text_len = len(text)
    text = '| %s |' % text
    print_there(1, width - len(text) + 1, '+%s+' % ('-' * (text_len + 2)))
    print_there(2, width - len(text) + 1, text)
    print_there(3, width - len(text) + 1, '+%s+' % ('-' * (text_len + 2)))

