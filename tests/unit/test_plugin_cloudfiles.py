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

import unittest
from pyraxshell.plugins.plugin import Plugin  # @UnresolvedImport


class Test(unittest.TestCase):

    def test_upload(self):
        p = Plugin()

        line = 'upload src:/tmp/rs.jpg dest:02/rs-logo.jpg'
        p.parseline(line)
        print "XX", p.arg
        self.assertEqual(p.kvarg, {'src': '/tmp/rs.jpg',
                                   'dest': '02/rs-logo.jpg'})
        self.assertEqual(p.varg, [])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
