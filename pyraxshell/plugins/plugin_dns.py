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

name = 'dns'

def injectme(c):
    setattr(c, 'do_dns', do_dns)
    logging.debug('%s injected' % __file__)

def do_dns(*args):
    Cmd_DNS().cmdloop()


class Cmd_DNS(cmd.Cmd):
    '''
    pyrax shell POC - DNS module
    '''
    
    prompt = "H dns>"    # default prompt
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.libplugin = LibDNS()

    def do_EOF(self, line): 
        '''
        just press CTRL-D to quit this menu
        '''
        print
        return True
    
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
                logging.error('\'%s\' is not a valid IP v4 address' % data)
                return False
        else:
            logging.warn("data missing")
            return False
        if 'ttl' in d_kv.keys():
            ttl = d_kv['ttl']
        else:
            logging.warn("ttl missing")
        rec = { "type": _type,
                "name": name,
                "data": data,
                "ttl": ttl}
        try:
            (new_rec_data, domain_name) = name.split('.', 1)
            logging.debug("add '%s' in domain '%s'" %
                          (new_rec_data, domain_name))
            dom = dns.find(name=domain_name)
            try:
                logging.info("adding dns record name:%s, type:%s, data:%s, ttl:%s" %
                             (name, _type, data, ttl))
                dom.add_record(rec)
            except pyrax.exceptions.DomainRecordAdditionFailed:
                logging.error("duplicate dns record '%s'" % name)
        except exc.NotFound:
            logging.error("domain '%s' not found" % name)
    
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
        (name, email_address, ttl, comment) = (None, None, None, None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            logging.warn("name missing")
            return False
        if 'email_address' in d_kv.keys():
            email_address = d_kv['email_address']
        else:
            logging.warn("email_address missing")
            return False
        if 'ttl' in d_kv.keys():
            ttl = d_kv['ttl']
        else:
            logging.warn("ttl missing, using default value")
            ttl = 900
        if 'comment' in d_kv.keys():
            comment = d_kv['comment']
        else:
            logging.warn("comment missing, using default value")
        self.libplugin.create_domain(name, email_address, ttl, comment)
    
    def complete_create_domain(self, text, line, begidx, endidx):
        params = ['name:', 'emanameil_address:', 'ttl:', 'comment:']
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_create_ptr_record(self, line):
#TODO -- 
        '''
        create a PTR record
        '''
        logging.info('NOT IMPLEMENTED YET')
    
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
        (name, email_address, ttl, comment) = (None, None, None, None)
        # parsing parameters
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            logging.warn("name missing")
            return False
        if 'email_address' in d_kv.keys():
            email_address = d_kv['email_address']
        else:
            logging.warn("email_address missing")
            return False
        if 'ttl' in d_kv.keys():
            ttl = d_kv['ttl']
        else:
            logging.warn("ttl missing, using default value")
            ttl = 900
        if 'comment' in d_kv.keys():
            comment = d_kv['comment']
        else:
            logging.warn("comment missing, using default value")
        try:
            subdomain_name = name
            domain_name = subdomain_name.split('.', 1)[1]
            logging.debug("creating subdomain '%s' in domain '%s'" %
                          (subdomain_name, domain_name))
            dns = pyrax.cloud_dns
            dns.find(name=domain_name)
            try:
                self.libplugin.create_domain(name, email_address, ttl, comment)
            except Exception:
                logging.error("cannot create domain '%s'" % domain_name)
        except exc.NotFound:
            logging.error("domain '%s' not found" % domain_name)
    
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
        
        type    record type, currently supported: A, MX
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
            logging.warn("type missing")
            return False
        if 'name' in d_kv.keys():
            name = d_kv['name']
        else:
            logging.warn("name missnameing")
            return False
        if 'data' in d_kv.keys():
            data = d_kv['data']
            if not is_ipv4(data):
                logging.error('\'%s\' is not a valid IP v4 address' % data)
                return False
        else:
            logging.warn("data missing")
            return False
        try:
            (del_rec_data, domain_name) = name.split('.', 1)
            logging.debug("delete '%s' in domain '%s'" %
                          (del_rec_data, domain_name))
            dom = dns.find(name=domain_name)
            try:
                for r in dom.list_records():
                    if r.name == name and r.type == _type and r.data == data:
                        r.delete()
            except:
                logging.error("cannot delete dns record '%s'" % name)
        except exc.NotFound:
            logging.error("domain '%s' not found" % name)
    
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
            logging.warn("domain_name missing")
            return False
        dns = pyrax.cloud_dns
        try:
            dom = dns.find(name=domain_name)
        except exc.NotFound:
            logging.warn("domain '%s' does not exist" % domain_name)
            return False
        
        sub_iter = dns.get_record_iterator(dom)
        [sub.delete() for sub in sub_iter if sub.type != "NS"]
    
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
            logging.warn("domain_name missing")
            return False
        dns = pyrax.cloud_dns
        try:
            dom = dns.find(name=domain_name)
            try:
                dom.delete()
                print "The domain '%s' was successfully deleted." % domain_name
            except:
                logging.error("it was not possible to delete '%s' domain "%
                              domain_name)
        except exc.NotFound:
            logging.warn("There is no DNS information for the domain '%s'." %
                         domain_name)
    
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
    
    def do_delete_ptr_record(self, line):
#TODO -- 
        '''
        delete a PTR record
        '''
        logging.info('NOT IMPLEMENTED YET')
    
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
            logging.warn("domain_name missing")
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
            print pt
        except exc.NotFound:
            logging.warn("no DNS information for the domain '%s'" %
                         domain_name)
        except Exception as e:
            logging.error(pprint.pformat(e))
            logging.error(str(e))
    
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
    
    def do_list_domains(self, line):
        '''
        list domains
        '''
        logging.debug('listing dns domains')
        dns = pyrax.cloud_dns
        domains = dns.list()
        try:
            header = ['name', 'email address', 'created']
            pt = PrettyTable(header)
            for d in domains:
                pt.add_row([d.name, d.emailAddress, d.created])
                logging.debug(pprint.pformat(d))
            pt.align['name'] = 'l'
            pt.align['email address'] = 'l'
            pt.get_string(sortby='name')
            print pt
        except:
            logging.error('cannot list dns domains')
    
    def do_list_ptr_records(self, line):
#TODO -- 
        '''
        list PTR records
        '''
        logging.info('NOT IMPLEMENTED YET')
    
    def do_list_subdomains(self, line):
#TODO -- 
        '''
        list subdomains
        '''
        logging.info('NOT IMPLEMENTED YET')
    
    def preloop(self):
        cmd.Cmd.preloop(self)
        logging.debug("preloop")
        import plugins.libauth
        if not plugins.libauth.LibAuth().is_authenticated():
            logging.warn('please, authenticate yourself before continuing')
