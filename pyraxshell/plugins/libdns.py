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
import traceback


class LibDNS(object):
    '''
    pyraxshell DNS library
    '''

    # ########################################
    # DNS

    def create_domain(self, domain_name, email_address, ttl, comment):
        '''
        create a domain
        '''
        try:
            logging.debug('creating dns domain name:%s, emailAddress:%s,'
                          'ttl:%s, comment:%s' %
                          (domain_name, email_address, ttl, comment))
            dns = pyrax.cloud_dns
            dom = dns.create(name=domain_name,
                             emailAddress=email_address,
                             ttl=ttl,
                             comment=comment)
            logging.info("domain created: %s" % dom)
            return True
        except exc.DomainCreationFailed as e:
            logging.error("domain creation failed: %s" % e)
            return False
        except Exception as e:
            logging.error("error: %s" % e)
            return False

    def get_domain_by_name(self, domain_name):
        '''
        return domain by name
        '''
        try:
            cdns = pyrax.cloud_dns
            domain = [d for d in cdns.list() if d.name == domain_name][0]
            return domain
        except IndexError:
            logging.error('cannot find domain name: \'%s\'' % domain_name)
            return False
        except:
            tb = traceback.format_exc()
            logging.error(tb)
            return False

    def get_domains(self):
        '''
        return domains
        '''
        dns = pyrax.cloud_dns
        return dns.list()

    def is_parent(self, record, domain):
        '''
        check if record is a child of domain
        '''
        record_tokens = record.split('.')
        domain_tokens = domain.split('.')
        if len(record_tokens) <= len(domain_tokens):
            return False
        for i in range(1, len(domain_tokens) + 1):
            if domain_tokens[-i] != record_tokens[-i]:
                return False
        return True

    def list_domain_names(self):
        '''
        return list of domain names
        '''
        dns = pyrax.cloud_dns
        return [d.name for d in dns.list()]

    def missing_subdomains(self, record, domain):
        '''return missing subdomains as a difference between given record and
           domain

        i.e.: record:foo.bar.example.com, domain:example.com -> bar.example.com

        record    DNS record as string
        domain    domain as string

        return None if record is not within domain
        '''
        if record == domain:
            return []
        if not self.is_parent(record, domain):
            return None
        record_tokens = record.split('.')
        domain_tokens = domain.split('.')
        diff = record_tokens[1:]
        for i in range(1, len(domain_tokens) + 1):
            if domain_tokens[-i] != record_tokens[-i]:
                return False
            diff.pop()
        for i in range(len(diff)):
            for j in range(0, i):
                diff[j] += '.' + diff[-i]
        for i in range(len(diff)):
            diff[i] = diff[i] + '.' + domain
        return diff

    def nearest_domain(self, record, domains):
        '''return the nearest domain in domains for record


        i.e.:

        domains = [ "bar.example.co.uk", "example.co.uk", "example.com",
                    "someexample.com", "example.bar.com", "bar.example.com"]
        record = "foo.bar.example.com"
        ...
        return 'bar.example.com'

        record    DNS record as string
        domains   list of domains as string
        '''
        biggest_match = 0
        actual_domain = ""
        for domain in domains:
            domparts = domain.split(".")
            recparts = record.split(".")
            domparts.reverse()
            i = len(recparts) - 1
            matches = 0
            for dompart in domparts:
                if recparts[i] == dompart:
                    matches += 1
                i -= 1
            domain_num_tokens = len(domain.split('.'))
            if (matches >= biggest_match) and (matches >= domain_num_tokens):
                biggest_match = matches
                actual_domain = domain
        msg = lambda s1, s2, s3: ("record '%s', domains:'%s', the nearest "
                                  "domain:'%s'" % (s1, s2, s3))
        logging.debug(msg(record, ', '.join([d for d in domains]),
                          actual_domain))
        return actual_domain
