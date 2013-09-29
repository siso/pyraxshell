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

import time
import threading
from utility import print_top_right
from globals import msg_queue

class Notifier(threading.Thread):
    '''
    A consumer class which get stuff from the Message Queue 'msg_queue'
    
    By default Notifier poll the queue every second, get messages, and
    print them one at a time. For the time being 'Producers' should not put
    more that one message per second on the queue
    '''
    def __init__(self, polltime=1):
        self.polltime = polltime
        # 'terminate' causes the thread to stop
        self._terminate = False
#         threading.Thread.setName('notifier')
        threading.Thread.__init__(self)
 
    @property
    def terminate(self):
        return self._terminate
    
    @terminate.setter
    def terminate(self, value=True):
        self._terminate = value
           
    def run(self):
        while True:
            # pop an item from the queue, if any
            if not msg_queue.empty():
                print_top_right(msg_queue.get())
            if self._terminate == True:
                break
            time.sleep(self.polltime)
        
        