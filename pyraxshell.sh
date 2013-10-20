#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of Rackspace DSE repository.
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.

# see: https://rackspacecloud.zendesk.com/tickets/1493675

import runpy, sys

saved_argv = sys.argv
runpy.run_path('pyraxshell/__main__.py', run_name="mainX")
sys.argv = saved_argv # restore sys.argv
