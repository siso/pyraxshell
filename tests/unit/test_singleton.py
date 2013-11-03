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

# usage:    $ python -m tests.unit.test_singleton

import unittest
from pyraxshell.singleton import Singleton  # @UnresolvedImport


@Singleton
class Foo:
    def __init__(self):
#         print 'Foo created'
        pass

class SingletonTest(unittest.TestCase):


    def test_foo_contructor(self):
        # Error, this isn't how you get the instance of a singleton
        self.assertRaises(TypeError, Foo)

    def test_foo_instance(self):
        f = Foo.Instance() # Good. Being explicit is in line with the Python Zen
        g = Foo.Instance() # Returns already created instance
        self.assertIs(f, g)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
