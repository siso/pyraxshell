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

import logging
import pyrax
import pyrax.exceptions as exc

class LibDNS(object):
    '''
    pyraxshell DNS library
    '''
    
    # ########################################
    # DNS
    
    def create_domain(self, domain_name, email_address, ttl, comment):
        try:
            logging.debug('creating dns domain name:%s, emailAddress:%s,'
                          'ttl:%s, comment:%s' %
                          (domain_name, email_address, ttl, comment))
            dns = pyrax.cloud_dns
            dom = dns.create(name = domain_name,
                             emailAddress = email_address,
                             ttl = ttl,
                             comment = comment)
            logging.info("domain created: %s" % dom)
            return True
        except exc.DomainCreationFailed as e:
            logging.error("domain creation failed: %s" % e)
            return False
        except Exception as e:
            logging.error("error: %s" % e)
            return False
