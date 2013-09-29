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
from utility import kvstring_to_dict, print_top_right
import threading
import uuid
import time
from plugin import Plugin 
from globals import msg_queue

name = 'test'

def injectme(c):
#     logging.debug(c)
#     logging.debug(dir(c))
#     
#     c.do_test = do_test
    setattr(c, 'do_test', do_test)
    logging.debug('%s injected' % __file__)
#     
#     logging.debug('c.get_names(): %s' % c.get_names())

def do_test(*args):
#     logging.debug("line: %s" % line)
    TestPlugin().cmdloop()


class TestPlugin(Plugin, cmd.Cmd):
    """
    pyraxshell - Test Plugin 
    """
    prompt = "RS %s>" % name    # default prompt

    def do_test(self, line):
        '''
        provide credentials and authenticate
        '''
        logging.debug("line: %s" % line)
        logging.info("TEST PLUGIN -- do_test")
    
    def do_run_test_thread(self, line):
        TestThread().start()
    
    def do_run_test_thread1(self, line):
        TestThread1().start()


class TestThread (threading.Thread):
    def __init__(self, threadID = uuid.uuid4()):
        '''
        test thread
        '''
        threading.Thread.__init__(self)
        self.threadID = threadID
        logging.debug('thread id:%s' % (threadID))
    
    def run(self):
        logging.debug("Starting %s" % self.threadID)
        max_rep = 5
        for i in range(max_rep):  # @UnusedVariable
            print_top_right(time.strftime('%H:%M:%S'))
            time.sleep(1)
        print_top_right('task completed')


class TestThread1 (threading.Thread):
    def __init__(self, threadID = uuid.uuid4()):
        '''
        test thread 1
        '''
        threading.Thread.__init__(self)
        self.threadID = threadID
        logging.debug('thread id:%s' % (threadID))
        # 'terminate' causes the thread to stop
        self._terminate = False
#         threading.Thread.setName('TestThread1')
        
    def run(self):
        logging.debug("Starting %s" % self.threadID)
        max_rep = 5
        for i in range(max_rep):  # @UnusedVariable
            msg_queue.put("thread %d - %s" % (self.threadID,
                                               time.strftime('%H:%M:%S')))
            time.sleep(1)
            if self._terminate == True:
                logging.debug("terminating thread %s" % self.name)
                return
        msg_queue.put('TestThread1 - task completed')

    @property
    def terminate(self):
        return self._terminate
    
    @terminate.setter
    def terminate(self, value=True):
        self._terminate = value
