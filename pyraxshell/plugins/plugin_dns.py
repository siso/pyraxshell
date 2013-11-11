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

import cmd
import logging
import pprint
import pyrax
import pyrax.exceptions as exc
from prettytable import PrettyTable
import traceback

from pyraxshell.globals import ERROR, WARN, INFO
from pyraxshell.plugins.libdns import LibDNS
from pyraxshell.utility import kvstring_to_dict, is_ipv4
import pyraxshell.plugins.plugin


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    '''
    pyrax shell POC - DNS module
    '''

    prompt = "RS dns>"  # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
        self.libplugin = LibDNS()

    # ########################################
    # CLOUD DNS

    def do_add_record(self, line):
        '''
        add DNS record

        type    record type, currently supported: A
        name    domain name
        data    i.e.: 1.2.3.4name
        ttl     TTL (optional, default:900)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'type', 'required': True},
            {'name': 'name', 'required': True},
            {'name': 'data', 'required': True},
            {'name': 'ttl', 'default': 900}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok
        # additional checks
        if not is_ipv4(self.kvarg['data']):
            cmd_out = ('\'%s\' is not a valid IP v4 address' %
                       self.kvarg['data'])
            self.r(1, cmd_out, WARN)
            return False

        dns = pyrax.cloud_dns

        rec = {"type": self.kvarg['type'],
               "name": self.kvarg['name'],
               "data": self.kvarg['data'],
               "ttl": self.kvarg['ttl']}
        # create missing subdomains
        domains = self.libplugin.list_domain_names()
        nearest_domain = self.libplugin.nearest_domain(self.kvarg['name'],
                                                       domains)
        if nearest_domain is None:
            cmd_out = 'no matching domain found'
            self.r(1, cmd_out, ERROR)
            return False
        logging.debug('nearest_domain:%s' % nearest_domain)
        missing_subdomains = (self.libplugin.missing_subdomains
                              (self.kvarg['name'], nearest_domain))
        logging.info("creating missing domains: ", missing_subdomains)
        nearest_domain_obj = self.libplugin.get_domain_by_name(nearest_domain)
        for subdomain in missing_subdomains:
            self.libplugin.create_domain(subdomain,
                                         nearest_domain_obj.emailAddress,
                                         nearest_domain_obj.ttl,
                                         ''  # comment
                                         )
        try:
            (new_rec_data, domain_name) = self.kvarg['name'].split('.', 1)
            logging.debug("add '%s' in domain '%s'" %
                          (new_rec_data, domain_name))
            dom = dns.find(name=domain_name)
            try:
                dom.add_record(rec)
                cmd_out = ("adding dns record name:%s, type:%s, data:%s, "
                           "ttl:%s" % (self.kvarg['name'], self.kvarg['type'],
                                       self.kvarg['data'], self.kvarg['ttl']))
                self.r(0, cmd_out, INFO)
            except pyrax.exceptions.DomainRecordAdditionFailed:
                cmd_out = "duplicate dns record '%s'" % self.kvarg['name']
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = "domain '%s' not found" % self.kvarg['name']
            self.r(1, cmd_out, ERROR)

    def complete_add_record(self, text, line, begidx, endidx):
        params = ['data:', 'name:', 'ttl:', 'type:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_create_domain(self, line):
        '''
        create a domain

        Parameters:

        name       name of the domain
        email_address
        ttl                TTL (optional, default:900)
        comment            (optional, default:void)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'name', 'required': True},
            {'name': 'email_address', 'required': True},
            {'name': 'ttl', 'default': 900},
            {'name': 'comment', 'default': ''}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        self.libplugin.create_domain(self.kvarg['name'],
                                     self.kvarg['email_address'],
                                     self.kvarg['ttl'], self.kvarg['comment'])
        cmd_out = "domain added"
        self.r(0, cmd_out, INFO)

    def complete_create_domain(self, text, line, begidx, endidx):
        params = ['name:', 'email_address:', 'ttl:', 'comment:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

#     def do_create_ptr_record(self, line):
# #TODO --
#         '''
#         create a PTR record
#         '''
#         logging.info('NOT IMPLEMENTED YET')

    def do_create_subdomain(self, line):
        '''
        create a subdomain

        name     name of the subdomain
        email_address
        ttl                TTL (optional, default:900)
        comment            (optional, default:void)
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'name', 'required': True},
            {'name': 'email_address', 'required': True},
            {'name': 'ttl', 'default': 900},
            {'name': 'comment', 'default': ''}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            subdomain_name = self.kvarg['name']
            domain_name = subdomain_name.split('.', 1)[1]
            dns = pyrax.cloud_dns
            dns.find(name=domain_name)
            try:
                self.libplugin.create_domain(self.kvarg['name'],
                                             self.kvarg['email_address'],
                                             self.kvarg['ttl'],
                                             self.kvarg['comment'])
                cmd_out = ("created subdomain '%s' in domain '%s'" %
                           (subdomain_name, domain_name))
                self.r(0, cmd_out, INFO)
            except Exception:
                cmd_out = "cannot create domain '%s'" % domain_name
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = "domain '%s' not found" % domain_name
            self.r(1, cmd_out, ERROR)

    def complete_create_subdomain(self, text, line, begidx, endidx):
        params = ['name:', 'email_address:', 'ttl:', 'comment:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_delete_record(self, line):
        '''
        delete DNS record

        type    record type, currently supported: A
        name    domain name
        data    i.e.: 1.2.3.4
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'type', 'required': True},
            {'name': 'name', 'required': True},
            {'name': 'data', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok
        # additional checks
        if self.kvarg['type'] != 'A' and self.kvarg['type'] != 'MX':
            cmd_out = "type not supported"
            self.r(1, retmsg, ERROR)
            return False
        if not is_ipv4(self.kvarg['data']):
            cmd_out = ('\'%s\' is not a valid IP v4 address' %
                       self.kvarg['data'])
            self.r(1, cmd_out, ERROR)
            return False
        try:
            dns = pyrax.cloud_dns
            (del_rec_data, domain_name) = self.kvarg['name'].split('.', 1)
            dom = dns.find(name=domain_name)
            try:
                for r in dom.list_records():
                    if (r.name == self.kvarg['name'] and
                            r.type == self.kvarg['type'] and
                            r.data == self.kvarg['data']):
                        r.delete()
                cmd_out = ("delete '%s' in domain '%s'" % (del_rec_data,
                                                           domain_name))
                self.r(0, cmd_out, INFO)
            except:
                cmd_out = "cannot delete dns record '%s'" % self.kvarg['name']
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = "domain '%s' not found" % self.kvarg['name']
            self.r(1, cmd_out, ERROR)

    def complete_delete_record(self, text, line, begidx, endidx):
        params = ['data:', 'name:', 'type:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_delete_records(self, line):
        '''
        delete all DNS record but NS

        domain_name       name of the domain
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck({'name': 'domain_name',
                                           'required': True})
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        dns = pyrax.cloud_dns
        try:
            dom = dns.find(name=self.kvarg['domain_name'])
        except exc.NotFound:
            cmd_out = "domain '%s' does not exist" % self.kvarg['domain_name']
            self.r(1, cmd_out, ERROR)
            return False

        sub_iter = dns.get_record_iterator(dom)
        [sub.delete() for sub in sub_iter if sub.type != "NS"]
        cmd_out = "dns record deleted"
        self.r(0, cmd_out, INFO)

    def complete_delete_records(self, text, line, begidx, endidx):
        params = ['domain_name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_delete_domain(self, line):
        '''
        delete a domain

        domain_name       name of the domain to create
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'domain_name', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        dns = pyrax.cloud_dns
        try:
            dom = dns.find(name=self.kvarg['domain_name'])
            try:
                dom.delete()
                cmd_out = ("The domain '%s' was successfully deleted." %
                           self.kvarg['domain_name'])
                self.r(0, cmd_out, INFO)
            except:
                cmd_out = ("it was not possible to delete '%s' domain " %
                           self.kvarg['domain_name'])
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = ("There is no DNS information for the domain '%s'." %
                       self.kvarg['domain_name'])
            self.r(0, cmd_out, INFO)

    def complete_delete_domain(self, text, line, begidx, endidx):
        params = ['domain_name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

#     def do_delete_ptr_record(self, line):
# #TODO --
#         '''
#         delete a PTR record
#         '''
#         logging.info('NOT IMPLEMENTED YET')

#     def do_delete_subdomain(self, line):
#         '''
#         delete subdomain
#
#         name            subdomain name
#         '''
#         dns = pyrax.cloud_dns
#         try:
#             dom = dns.find(name=domain_name)
#         except exc.DomainCreationFailed as e:
#             logging.error('domain \'%s\' not found' % s name)

    def do_exit(self, *args):
        return True

    def do_list_records(self, line):
        '''
        list DNS records

        domain_name       name of the domain to create
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'domain_name', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        dns = pyrax.cloud_dns
        try:
            import time
            time.sleep(2)
            dom = dns.find(name=self.kvarg['domain_name'])
            pt = PrettyTable(['domain name', 'type', 'ttl', 'data'])
            for r in dom.list_records():
                logging.debug(pprint.pformat(r))
                pt.add_row([r.name, r.type, r.ttl, r.data])
            pt.get_string(sortby='data')
            pt.get_string(sortby='type')
            pt.align['domain name'] = 'l'
            pt.align['data'] = 'l'
            self.r(0, str(pt), INFO)
        except exc.NotFound:
            cmd_out = ("no DNS information for the domain '%s'" %
                       self.kvarg['domain_name'])
            self.r(1, cmd_out, ERROR)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False

    def complete_list_records(self, text, line, begidx, endidx):
        params = ['domain_name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions

    def do_list(self, line):
        '''
        list domains
        '''
        self.do_list_domains(line)

    def do_list_domains(self, line):
        '''
        list domains
        '''
        logging.debug('listing dns domains')
        dns = pyrax.cloud_dns
        domains = dns.list()
        try:
            header = ['id', 'name', 'email address', 'created', 'ttl']
            pt = PrettyTable(header)
            for d in domains:
                pt.add_row([d.id, d.name, d.emailAddress, d.created, d.ttl])
                logging.debug(pprint.pformat(d))
            pt.align['name'] = 'l'
            pt.align['email address'] = 'l'
            pt.get_string(sortby='name')
            self.r(0, str(pt), INFO)
        except:
            logging.error('cannot list dns domains')
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

#     def do_list_ptr_records(self, line):
# #TODO --
#         '''
#         list PTR records
#         '''
#         logging.info('NOT IMPLEMENTED YET')

    def do_list_subdomains(self, line):
        '''
        list subdomains

        domain_name    name of the domain for which to list sub-domains
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name': 'domain_name', 'required': True}
        )
        if not retcode:  # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        self.r(0, retmsg, INFO)  # everything's ok

        try:
            domain = (self.libplugin.get_domain_by_name(self.
                                                        kvarg['domain_name']))
            subdomains = domain.list_subdomains()
            header = ['id', 'name', 'email address']
            pt = PrettyTable(header)
            for d in subdomains:
                pt.add_row([d.id, d.name, d.emailAddress])
                logging.debug(pprint.pformat(d))
            pt.align['name'] = 'l'
            pt.align['email address'] = 'l'
            pt.get_string(sortby='name')
            self.r(0, str(pt), INFO)
        except:
            logging.debug('cannot list \'%s\' sub-domains' %
                          self.kvarg['domain_name'])
            tb = traceback.format_exc()
            logging.error(tb)

    def complete_list_subdomains(self, text, line, begidx, endidx):
        params = ['domain_name:']
        if not text:
            completions = params[:]
        else:
            completions = [f for f in params if f.startswith(text)]
        return completions
