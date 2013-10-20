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
import sys
import terminalsize
import threading
import traceback
import uuid

from ansicolours import ANSIColours
from configuration import Configuration
from globals import *  # @UnusedWildImport


def check_dir_home():
    '''
    check and create missing dirs and files
    '''
    if not os.path.isdir(os.path.expanduser(HOME_DIR)):
        # create dirs and config files
        check_dir(os.path.expanduser(HOME_DIR))
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

def get_ip_family(address):
    '''
    obtain the address family an IP belongs to
    '''
    if is_ipv4(address):
        return 'ipv4'
    elif is_ipv6(address):
        return 'ipv6'
    return None

def get_uuid():
    return uuid.uuid4()

def kvstring_to_dict(kvs):
    '''
    DEPRECATED - use 'plugins.Plugin._kvarg' instead
    
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
        tb = traceback.format_exc()
        logging.error(tb)
    return d_out

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

def l(cmd, retcode, msg, log_level):
    '''
    logging message facility which logs and returns log message
    
    cmd        command-line with params
    retcode    command return-code
    msg        informative message
    log_level  log level of the message
    '''
    logging.debug("[IN] %s" % cmd)
    logging.debug("[OUT] %s, log_level:%d" % (msg, log_level))
    interactive = Configuration.Instance().interactive  # @UndefinedVariable
    if interactive:
        c = ANSIColours.Instance()  # @UndefinedVariable
    if log_level == DEBUG:
        if not interactive:
            msg = "0|%s" % msg
        else:
            msg = "%s%s%s" % (c.get('white'), msg, c.endc)
        logging.debug(msg)
    if log_level == INFO:
        if not interactive:
            msg = "0|%s" % msg
        else:
            msg = "%s%s%s" % (c.get('blue'), msg, c.endc)
        logging.info(msg)
    if log_level == WARN:
        if not interactive:
            msg = "0|%s" % msg
        else:
            msg = "%s%s%s" % (c.get('magenta'), msg, c.endc)
        logging.warn(msg)
    if log_level == ERROR:
        if not interactive:
            msg = "1|%s" % msg
        else:
            msg = "%s%s%s" % (c.get('red'), msg, c.endc)
        logging.error(msg)
    if log_level == CRITICAL:  # @UndefinedVariable
        if not interactive:
            msg = "1|%s" % msg
        else:
            msg = "%s%s%s" % (c.get('red', True), msg, c.endc)
        logging.critical(msg)
    return msg

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
#TODO - display multi-line messages
    (width, heigth) = terminalsize.get_terminal_size()  # @UnusedVariable
    text_len = len(text)
    text = '| %s |' % text
    print_there(1, width - len(text) + 1, '+%s+' % ('-' * (text_len + 2)))
    print_there(2, width - len(text) + 1, text)
    print_there(3, width - len(text) + 1, '+%s+' % ('-' * (text_len + 2)))

def terminate_threads():
    '''
    stop threads gracefully 
    '''
    logging.debug("terminate threads gracefully and exit")
    logging.debug('%d threads running' % len(threading.enumerate()))
    for t in threading.enumerate():
        if hasattr(t, '_terminate'):
            logging.debug('terminating thread: %s' % t.getName())
            t.terminate = True
    sys.exit(0)
