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
from pyraxshell.utility import is_ipv4, is_ipv6  # @UnresolvedImport
from pyraxshell.utility import str_ip_version   # @UnresolvedImport


class Test(unittest.TestCase):


    def test_is_ipv4(self):
        self.assertTrue(is_ipv4('0.0.0.0'))
        self.assertFalse(is_ipv4('0.0.0.999'))
        self.assertFalse(is_ipv4('THIS IS NOT AN IP ADDRESS!'))
        self.assertFalse(is_ipv4('2a00:1a48:7806:0116:b1ee:476b:ff08:7bb4'))

    def test_is_ipv6(self):
        self.assertFalse(is_ipv6('0.0.0.0'))
        self.assertFalse(is_ipv6('0.0.0.999'))
        self.assertFalse(is_ipv6('THIS IS NOT AN IP ADDRESS!'))
        self.assertTrue(is_ipv6('2a00:1a48:7806:0116:b1ee:476b:ff08:7bb4'))
    
    def test_str_ip_version(self):
        self.assertEquals(str_ip_version('0.0.0.0'), 'ipv4')
        self.assertEquals(str_ip_version('2a00:1a48:7806:0116:b1ee:476b:ff08:7bb4'), 'ipv6')
        self.assertEquals(str_ip_version('THIS IS NOT AN IP ADDRESS!'), None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()