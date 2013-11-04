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

from mock import MagicMock

import unittest
import pyraxshell.version
from pyraxshell.version import check_version_file


class TestVersion(unittest.TestCase):
    '''
    Test version module
    '''

    def test_check_version_file(self):
        pyraxshell.version.read_version_file = MagicMock(return_value='0.0.0')
        pyraxshell.version.VERSION = MagicMock(return_value='0.0.1')
        self.assertFalse(check_version_file())

        pyraxshell.version.read_version_file = MagicMock(return_value='0.0.0')
        pyraxshell.version.VERSION = MagicMock(return_value='0.0.0')
        self.assertFalse(check_version_file())

        pyraxshell.version.read_version_file = MagicMock(return_value='WRONG')
        pyraxshell.version.VERSION = MagicMock(return_value='0.0.0')
        self.assertFalse(check_version_file())

        pyraxshell.version.read_version_file = MagicMock(return_value='')
        pyraxshell.version.VERSION = MagicMock(return_value='0.0.0')
        self.assertFalse(check_version_file())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
