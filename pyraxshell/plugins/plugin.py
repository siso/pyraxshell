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


class Plugin(cmd.Cmd):
    '''
    Plugin base class
    '''

    def __init__(self):
        '''
        Constructor
        '''
        cmd.Cmd.__init__(self)
    
    def do_EOF(self, line):
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True
    
    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')

    def do_exit(self,*args):
        '''
        exit this interpreter
        '''
        return True
        
    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
