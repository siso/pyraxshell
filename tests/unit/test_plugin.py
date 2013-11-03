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


    def test_parseline(self):
        p = Plugin()

        line = 'foocommand'
        p.parseline(line)
        self.assertEqual(p.cmd, "foocommand")
        self.assertEqual(p.arg, "")
        self.assertEqual(p.line, "foocommand")

        line = 'foocommand fooarg'
        p.parseline(line)
        self.assertEqual(p.cmd, "foocommand")
        self.assertEqual(p.arg, "fooarg")
        self.assertEqual(p.line, "foocommand fooarg")

        line = 'foocommand a:b'
        p.parseline(line)
        self.assertEqual(p.cmd, "foocommand")
        self.assertEqual(p.arg, "a:b")
        self.assertEqual(p.line, "foocommand a:b")

        line = 'foocommand a:b c:d'
        p.parseline(line)
        self.assertEqual(p.cmd, "foocommand")
        self.assertEqual(p.arg, "a:b c:d")
        self.assertEqual(p.line, "foocommand a:b c:d")

        line = 'foocommand a:b foo c:d bar'
        p.parseline(line)
        self.assertEqual(p.cmd, "foocommand")
        self.assertEqual(p.arg, "a:b foo c:d bar")
        self.assertEqual(p.line, "foocommand a:b foo c:d bar")


#         _in = kvstring_to_dict("k0:v0             k1:v1 ki:vi")
#         _out = {'k0':'v0','k1':'v1','ki':'vi'}
#         self.assertItemsEqual(_in, _out)
#
#         _in = kvstring_to_dict("k0=v0             k1=v1 ki:vi")
#         _out = {'k0':'v0','k1':'v1','ki':'vi'}
#         self.assertItemsEqual(_in, _out)
#
#         _in = kvstring_to_dict("")
#         _out = {}
#         self.assertItemsEqual(_in, _out)
#
#         _in = "k0!v0"
#         self.assertRaises(TypeError, kvstring_to_dict(_in))
#
#         _in = "k0:"
#         self.assertRaises(TypeError, kvstring_to_dict(_in))

    def test_argparse(self):
        p = Plugin()

        line = 'foocommand'
        p.parseline(line)
        self.assertEqual(p.kvarg, {})
        self.assertEqual(p.varg, [])

        line = 'foocommand a:b'
        p.parseline(line)
        self.assertEqual(p.kvarg, {'a':'b'})
        self.assertEqual(p.varg, [])

        line = 'foocommand a'
        p.parseline(line)
        self.assertEqual(p.kvarg, {})
        self.assertEqual(p.varg, ['a'])

        line = 'foocommand a c:d e f:g'
        p.parseline(line)
        self.assertEqual(p.kvarg, {'c':'d', 'f':'g'})
        self.assertEqual(p.varg, ['a', 'e'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()