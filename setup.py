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

from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys

import pyraxshell

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

long_description = read('README.rst')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='pyrxshell',
    version=pyraxshell.__version__,
    url='http://github.com/siso/pyraxshell/',
    license='GPL 3',
    author='Simone Soldateschi',
    tests_require=['pytest'],
    install_requires=['pyrax=1.4.9',
                    ],
    cmdclass={'test': PyTest},
    author_email='simone.soldateschi@gmail.com',
    description='pyrax shell - manage OpenStack with a CLI tool',
    long_description=long_description,
    packages=['pyraxshell'],
    include_package_data=True,
    platforms='any',
    test_suite='pyraxshell.test.test_pyraxshell',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 0 - Beta',
        'Natural Language :: English',
        'Environment :: CLI tool',
        'Intended Audience :: DevOps and SysAdm',
        'License :: OSI Approved :: GPL 3 License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)

