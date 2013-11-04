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
from pyraxshell.plugins.libdns import LibDNS  # @UnresolvedImport


class Test(unittest.TestCase):

    def test_missing_subdomains(self):
        record = "foo.bar.example.co.uk"
        domain = "bar.example.com"
        self.assertEqual(None, LibDNS().missing_subdomains(record, domain))

        record = "bar.example.com"
        domain = "bar.example.com"
        self.assertEqual([], LibDNS().missing_subdomains(record, domain))

        record = "foo.bar.example.com"
        domain = "bar.example.com"
        self.assertEqual([], LibDNS().missing_subdomains(record, domain))

        record = "yyy.foo.bar.example.com"
        domain = "bar.example.com"
        self.assertEqual(['foo.bar.example.com'],
                         LibDNS().missing_subdomains(record, domain))

        record = "xxx.yyy.foo.bar.example.com"
        domain = "bar.example.com"
        self.assertEqual(['yyy.foo.bar.example.com', 'foo.bar.example.com'],
                         LibDNS().missing_subdomains(record, domain))

    def test_is_parent(self):
        libdns = LibDNS()
        self.assertTrue(libdns.is_parent('foo.bar.com', 'bar.com'))
        self.assertTrue(libdns.is_parent('yyy.foo.bar.com', 'bar.com'))
        self.assertFalse(libdns.is_parent('foo.bar.com', 'foo.bar.com'))
        self.assertFalse(libdns.is_parent('bar.com', 'foo.bar.com'))
        self.assertFalse(libdns.is_parent('yyy.foo.bar.com', 'bar.co.uk'))

    def test_nearest_domain(self):
        domains = ["bar.example.co.uk", "example.co.uk", "example.com",
                   "someexample.com", "example.bar.com", "bar.example.com"]

        record = "foo.bar.example.com"
        nearest_domain = LibDNS().nearest_domain(record, domains)
        self.assertEqual('bar.example.com', nearest_domain)

        record = "yyy.foo.bar.example.com"
        nearest_domain = LibDNS().nearest_domain(record, domains)
        self.assertEqual('bar.example.com', nearest_domain)

        record = "x.example.com"
        nearest_domain = LibDNS().nearest_domain(record, domains)
        self.assertEqual('example.com', nearest_domain)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
