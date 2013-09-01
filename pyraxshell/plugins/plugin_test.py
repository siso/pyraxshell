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

'''
Created on 1 Aug 2013

This is just a testing plugin developed to implement the plugin system.

To implement a plugin:

* assign a value to the 'name' attribute
* ...

@author: soldasimo
'''
import cmd
import logging

name = 'test'

def injectme(c):
#     logging.debug(c)
#     logging.debug(dir(c))
#     
#     c.do_test = do_test
    setattr(c, 'do_test', do_test)
#     
#     logging.debug('c.get_names(): %s' % c.get_names())
    logging.debug('plugin_test injected')

def do_test(*args):
    '''
    just testing
    '''
#     logging.debug("line: %s" % line)
    Plugin().cmdloop()

class Plugin(cmd.Cmd):
    """
    pyrax shell POC Test Plugin 
    """
    prompt = "H %s>" % name    # default prompt
    
    def do_exit(self,*args):
        return True

    def do_test(self, line):
        '''
        provide credentials and authenticate
        '''
        logging.debug("TEST PLUGIN -- do_test")
        logging.debug("line: %s" % line)
    
    def do_EOF(self, line):
        print
        return True
