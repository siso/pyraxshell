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
from utility import kvstring_to_dict, is_ipv4
from plugins.libdns import LibDNS
import pyrax
import pyrax.exceptions as exc
from prettytable import PrettyTable
import pprint
from plugin import Plugin
import traceback
from globals import ERROR, WARN, INFO

name = 'dns'

def injectme(c):
    setattr(c, 'do_dns', do_dns)
    logging.debug('%s injected' % __file__)

def do_dns(*args):
    Cmd_dns().cmdloop()


class Cmd_dns(Plugin, cmd.Cmd):
    '''
    pyrax shell POC - DNS module
    '''
    
    prompt = "RS dns>"    # default prompt
    
    def __init__(self):
        Plugin.__init__(self)
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
        dns = pyrax.cloud_dns
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_type, name, data, ttl) = (None, None, None, 900)
        # parsing parameters
        if 'type' in d_kv.keys():
            _type = d_kv['type']
            if _type != 'A':
                logging.warn("type not supported")
                return False
        else:
            logging.warn("type missing")
            return False
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            logging.warn("name missing")
            return False
        if 'data' in d_kv.keys():
            data = d_kv['data']
            if not is_ipv4(data):
                cmd_out = '\'%s\' is not a valid IP v4 address' % data
                self.r(1, cmd_out, WARN)
                return False
        else:
            cmd_out = "data missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'ttl' in d_kv.keys():
            ttl = d_kv['ttl']
        else:
            logging.warn("ttl missing, using default")
        rec = { "type": _type,
                "name": name,
                "data": data,
                "ttl": ttl}
        # create missing subdomains
        domains = self.libplugin.list_domain_names()
        nearest_domain = self.libplugin.nearest_domain(name, domains)
        if nearest_domain == None:
            cmd_out = 'no matching domain found'
            self.r(1, cmd_out, ERROR)
            return False
        logging.debug('nearest_domain:%s' % nearest_domain)
        missing_subdomains = self.libplugin.missing_subdomains(name, nearest_domain)
        logging.info("creating missing domains: ", missing_subdomains)
        nearest_domain_obj = self.libplugin.get_domain_by_name(nearest_domain)
        for subdomain in missing_subdomains:
            self.libplugin.create_domain(subdomain,
                                         nearest_domain_obj.emailAddress,
                                         nearest_domain_obj.ttl,
                                         ''     # comment
                                         )
        try:
            (new_rec_data, domain_name) = name.split('.', 1)
            logging.debug("add '%s' in domain '%s'" %
                          (new_rec_data, domain_name))
            dom = dns.find(name=domain_name)
            try:
                dom.add_record(rec)
                cmd_out = ("adding dns record name:%s, type:%s, data:%s, ttl:%s" %
                           (name, _type, data, ttl))
                self.r(0, cmd_out, INFO)
            except pyrax.exceptions.DomainRecordAdditionFailed:
                cmd_out = "duplicate dns record '%s'" % name
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = "domain '%s' not found" % name
            self.r(1, cmd_out, ERROR)
    
    def complete_add_record(self, text, line, begidx, endidx):
        params = ['data:', 'name:', 'ttl:', 'type:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
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
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (name, email_address, ttl, comment) = (None, None, 900, None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            cmd_out = "name missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'email_address' in d_kv.keys():
            email_address = d_kv['email_address']
        else:
            cmd_out = "email_address missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'ttl' in d_kv.keys():
            ttl = d_kv['ttl']
        else:
            logging.warn("ttl missing, using default value:%d" % ttl)
        if 'comment' in d_kv.keys():
            comment = d_kv['comment']
        else:
            logging.warn("comment missing, using default value")
        self.libplugin.create_domain(name, email_address, ttl, comment)
        cmd_out = "domain added"
        self.r(0, cmd_out, INFO)
    
    def complete_create_domain(self, text, line, begidx, endidx):
        params = ['name:', 'email_address:', 'ttl:', 'comment:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
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
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (name, email_address, ttl, comment) = (None, None, 900, None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            cmd_out = "name missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'email_address' in d_kv.keys():
            email_address = d_kv['email_address']
        else:
            cmd_out = "email_address missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'ttl' in d_kv.keys():
            ttl = d_kv['ttl']
        else:
            logging.warn("ttl missing, using default value: %d" % ttl)
        if 'comment' in d_kv.keys():
            comment = d_kv['comment']
        else:
            logging.warn("comment missing, using default value")
        try:
            subdomain_name = name
            domain_name = subdomain_name.split('.', 1)[1]
            dns = pyrax.cloud_dns
            dns.find(name=domain_name)
            try:
                self.libplugin.create_domain(name, email_address, ttl, comment)
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
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete_record(self, line):
        '''
        delete DNS record
        
        type    record type, currently supported: A
        name    domain name
        data    i.e.: 1.2.3.4
        '''
        dns = pyrax.cloud_dns
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (_type, name, data) = (None, None, None)
        # parsing parameters
        if 'type' in d_kv.keys():
            _type = d_kv['type']
            if _type != 'A' and _type != 'MX':
                logging.warn("type not supported")
                return False
        else:
            cmd_out = "type missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            cmd_out = "name missing"
            self.r(1, cmd_out, WARN)
            return False
        if 'data' in d_kv.keys():
            data = d_kv['data']
            if not is_ipv4(data):
                cmd_out = '\'%s\' is not a valid IP v4 address' % data
                self.r(1, cmd_out, ERROR)
                return False
        else:
            cmd_out = "data missing"
            self.r(1, cmd_out, WARN)
            return False
        try:
            (del_rec_data, domain_name) = name.split('.', 1)
            dom = dns.find(name=domain_name)
            try:
                for r in dom.list_records():
                    if r.name == name and r.type == _type and r.data == data:
                        r.delete()
                cmd_out = ("delete '%s' in domain '%s'" % (del_rec_data,
                                                           domain_name))
                self.r(0, cmd_out, INFO)
            except:
                cmd_out = "cannot delete dns record '%s'" % name
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = "domain '%s' not found" % name
            self.r(1, cmd_out, ERROR)
    
    def complete_delete_record(self, text, line, begidx, endidx):
        params = ['data:', 'name:', 'type:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete_records(self, line):
        '''
        delete all DNS record but NS
        
        domain_name       name of the domain
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (domain_name) = (None)
        # parsing parameters
        if 'domain_name' in d_kv.keys():
            domain_name = d_kv['domain_name']
        else:
            cmd_out = "domain_name missing"
            self.r(1, cmd_out, WARN)
            return False
        dns = pyrax.cloud_dns
        try:
            dom = dns.find(name=domain_name)
        except exc.NotFound:
            cmd_out = "domain '%s' does not exist" % domain_name
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
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_delete_domain(self, line):
        '''
        delete a domain
         
        domain_name       name of the domain to create
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (domain_name) = (None)
        # parsing parameters
        if 'domain_name' in d_kv.keys():
            domain_name = d_kv['domain_name']
        else:
            cmd_out = "domain_name missing"
            self.r(1, cmd_out, WARN)
            return False
        dns = pyrax.cloud_dns
        try:
            dom = dns.find(name=domain_name)
            try:
                dom.delete()
                cmd_out = ("The domain '%s' was successfully deleted." %
                           domain_name)
                self.r(0, cmd_out, INFO)
            except:
                cmd_out = ("it was not possible to delete '%s' domain " %
                           domain_name)
                self.r(1, cmd_out, ERROR)
        except exc.NotFound:
            cmd_out = ("There is no DNS information for the domain '%s'." %
                       domain_name)
            self.r(0, cmd_out, INFO)
    
    def complete_delete_domain(self, text, line, begidx, endidx):
        params = ['domain_name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
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
    
    def do_exit(self,*args):
        return True

    def do_list_records(self, line):
        '''
        list DNS records
         
        domain_name       name of the domain to create
        '''
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (domain_name) = (None)
        # parsing parameters
        if 'domain_name' in d_kv.keys():
            domain_name = d_kv['domain_name']
        else:
            cmd_out = "domain_name missing"
            self.r(1, cmd_out, WARN)
            return False
        dns = pyrax.cloud_dns
        try:
            import time
            time.sleep(2)
            dom = dns.find(name=domain_name)
            pt = PrettyTable(['domain name', 'type', 'ttl', 'data'])
            for r in dom.list_records():
                logging.debug(pprint.pformat(r))
                pt.add_row([r.name, r.type, r.ttl, r.data])
            pt.get_string(sortby='data')
            pt.get_string(sortby='type')
            pt.align['domain name'] = 'l'
            pt.align['data'] = 'l'
            self.r(0, pt, INFO)
        except exc.NotFound:
            cmd_out = ("no DNS information for the domain '%s'" %
                       domain_name)
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
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
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
            self.r(0, pt, INFO)
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
        logging.debug("line: %s" % line)
        d_kv = kvstring_to_dict(line)
        logging.debug("kvs: %s" % d_kv)
        # default values
        (domain_name) = (None)
        # parsing parameters
        if 'domain_name' in d_kv.keys():
            domain_name = d_kv['domain_name']
        else:
            cmd_out = "domain_name missing"
            self.r(1, cmd_out, WARN)
            return False
        logging.debug('listing \'%s\' sub-domains' % domain_name)
        try:
            domain = self.libplugin.get_domain_by_name(domain_name)
            subdomains = domain.list_subdomains()
            header = ['id', 'name', 'email address']
            pt = PrettyTable(header)
            for d in subdomains:
                pt.add_row([d.id, d.name, d.emailAddress])
                logging.debug(pprint.pformat(d))
            pt.align['name'] = 'l'
            pt.align['email address'] = 'l'
            pt.get_string(sortby='name')
            self.r(0, pt, INFO)
        except:
            logging.debug('cannot list \'%s\' sub-domains' % domain_name)
            tb = traceback.format_exc()
            logging.error(tb)

    def complete_list_subdomains(self, text, line, begidx, endidx):
        params = ['domain_name:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
