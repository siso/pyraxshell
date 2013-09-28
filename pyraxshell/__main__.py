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
from configuration import Configuration
import sys
import pyrax
import utility
from pyraxshell import Cmd_Pyraxshell
from globals import CONFIG_FILE
from utility import check_dir_home
from sessions import Sessions
from db import DB

def main():
    # check '~/.pyraxshell' and config files  exist, if not then create it
    if not check_dir_home():
        print ("This is the first time 'pyraxshell' runs, please, configure "
               "'%s' according to your needs" % CONFIG_FILE)
        #create db
        DB()
        Sessions.Instance().create_table_sessions()  # @UndefinedVariable
        Sessions.Instance().create_table_commands()  # @UndefinedVariable
        sys.exit(0)
    
    # ########################################
    # LOGGING
    utility.logging_start()  # @UndefinedVariable
    logging.debug('starting')
    
    # ########################################
    # CONFIGURATION
    cfg = Configuration.Instance()  # @UndefinedVariable
    cfg.parsecli(sys.argv)
    logging.debug("configuration: %s" % cfg)
    
    # ########################################
    # START SESSION
    Sessions.Instance().start_session()  # @UndefinedVariable
#     Sessions.Instance().insert_table_commands('IN', 'OUT')  # @UndefinedVariable
    
    # ########################################
    # DO STUFF
    # handle configuration
    if cfg.pyrax_http_debug:
        pyrax.set_http_debug(True)
    if cfg.pyrax_no_verify_ssl:
        # see: https://github.com/rackspace/pyrax/issues/187
        pyrax.set_setting("verify_ssl", False)
    Cmd_Pyraxshell().cmdloop()

if __name__ == '__main__':
    main()
