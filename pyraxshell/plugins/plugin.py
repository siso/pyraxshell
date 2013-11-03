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
import pprint
import re
import sys
import traceback

from pyraxshell.configuration import Configuration
from pyraxshell.globals import *  # @UnusedWildImport
from pyraxshell.sessions import Sessions
from pyraxshell.utility import l

name = 'none'


class Plugin(cmd.Cmd):
    '''
    Plugin base class
    '''
    
    prompt = "RS %s>" % name    # default prompt
    
    def __init__(self):
        '''
        Constructor
        '''
        cmd.Cmd.__init__(self)
        self.cfg = Configuration.Instance()  # @UndefinedVariable
        # current command
        self.cmd = None
        self.arg = None
        self.line = None
        
        # no 'Cmd' output in non-interactive mode
        interactive = os.isatty(0)
        if not interactive:
            f = open(os.devnull, 'w')
            sys.stdout = f
    
    def kvargcheck(self, *args):
        '''
        check 'self.kvarg' against passed check rules ('*args')
        
        Args:
            *args should be dictionaries as the following:
        
                {'name':'key-name', 'default|required':value}
        
        Returns:
            (bool, msg). The return code::
            
                True    -- Success!
                False   -- No good.
            and 'msg' is an informative message
        
        Example:
        
        The following code will ensure that 'self.kvarg' contains required
        parameters 'username' and 'apikey', and will default missing parameters
        to those provided.
        Additional parameters will be wiped out:
        
            retcode, retmsg = self.kvargcheck(
                  {'name':'identity_type', 'default':'rackspace'},
                  {'name':'username', 'required':True},
                  {'name':'apikey', 'required':True},
                  {'name':'region', 'default':'LON'}
            )
        
        So, to recap:
        
            IN: username:foo apikey:aa identity_type:openstack xx:yy TRUE
            OUT: username:foo apikey:aa identity_type:openstack region:LON
            
            IN: username:foo apikey:aa 
            OUT: username:foo apikey:aa identity_type:rackspace region:LON
        '''
        logging.debug('args: %s' % pprint.pformat(args))
        try:
            for d in args:
                if type(d) is type({}):
                    logging.debug('required param \'%s\'' % d['name'])
                    if not d['name'] in self.kvarg.keys():
                        if 'required' in d.keys():
                            logging.debug("retcode:False, missing '%s'" %
                                          d['name'])
                            return (False, "missing '%s'" % d['name'])
                        else:
                            self.kvarg[d['name']] = d['default']
                            logging.debug('added self.kvarg[\'%s\']:%s' %
                                          (d['name'], d['default']))
                else:
                    logging.debug('skipping: %s' % pprint.pformat(d))
            logging.debug("retcode:True, retmsg:ok")
            return True, "ok"
        except:
            logging.debug("retcode:False, retmsg:unknown problem occurred")
            return False, 'unknown problem occurred'
    
    def argparse(self):
        '''
        parse 'self.arg' and extract 'kvarg' and 'varg'
        
        self.arg can be the following:
        
        * a:b    --> added to 'self.kvarg'
        * x:$y   --> added to 'self.kvarg'
        * c      --> added to 'self.varg'
        
        transform a key-value-args string to kvargs dictionary
        key-value separator can be ':' or '=', even mixed, i.e.:
        
        "k0:v0 k1=v1 ... ki:vi" ==> {'k0':'v0','k1':'v1','ki':'vi'}
        
        This method is automatically called by 'self.parseline()'.    
        
        Returns:
        
        True  -- parsed correctly
        False -- No good
        '''
        self.kvarg, self.varg = {}, []
        if self.arg == None or len(self.arg) == 0:
            return None
        try:
            arg = self.arg
            arg = arg.replace('=', ':')
            for token in arg.split():
                # determine token type
                p1 = re.compile('^[a-zA-Z0-9_]+:[a-zA-Z0-9_~/\.\-@]+$')
                p2 = re.compile('^[a-zA-Z0-9_]+$')
                p3 = re.compile('^[a-zA-Z0-9_]+:\$[a-zA-Z0-9_]+$')
                if p1.match(token) or p3.match(token):
                    # 'a:b' or 'x:$y'
                    kv = token.split(':')
                    self.kvarg[kv[0]] = kv[1]
                elif p2.match(token):
                    # 'c'
                    self.varg.append(token)
                else:
                    logging.warn('cannot parse: \'%s\'' % token)
        except:
            tb = traceback.format_exc()
            logging.debug(tb)
            self.kvarg = None
        try:
            logging.debug("self.kvarg: %s" %
                          ', '.join('%s:%s' % (k,v)
                                    for k,v in self.kvarg.items()))
            logging.debug("self.varg: %s" %
                          ', '.join('%s' % v for v in self.varg))
        except:
            return None

    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')
    
    def parseline(self, line):
        '''
        override 'cmd.Cmd.parseline' to store cmd, arg and line
        '''
        # call superclass method
        self.cmd, self.arg, self.line = cmd.Cmd.parseline(self, line)
        # extract key:value pairs from args
        self.argparse()
        return self.cmd, self.arg, self.line

    def precmd(self, line):
        if not self.cfg.interactive:
            print
        return cmd.Cmd.precmd(self, line)
    
    def preloop(self):
        '''
        override preloop and verify if user is authenticated
        '''
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import pyraxshell.plugins.libauth
        if not pyraxshell.plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
    
    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True
    
    def do_dir(self, line):
        '''
        list alias
        '''
        return self.do_list(line)

    def do_exit(self, line):
        '''
        EOF alias
        '''
        return self.do_EOF(line)
    
    def do_list(self, line):
        '''
        default list method (this needs to be here to define aliases: ls, ll, dir)
        '''
    
    def do_ll(self, line):
        '''
        list alias
        '''
        return self.do_list(line)
    
    def do_ls(self, line):
        '''
        list alias
        '''
        return self.do_list(line)
    
    def do_emptyline(self, line):
        '''
        print a new empty line
        '''
        if self.cfg.interactive:
            print
        else:
            print "\n"
    
    def do_quit(self, line):
        '''
        EOF alias
        '''
        return self.do_EOF(line)

    def r(self, retcode, msg, log_level):
        '''
        record Session command input/output to 'commands' table, and
        logging message facility
        '''
        l(self.line, retcode, msg, log_level)
        Sessions.Instance().insert_table_commands(self.line ,   # @UndefinedVariable
                                                  msg, retcode, log_level)
