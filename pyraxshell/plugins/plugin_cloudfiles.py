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
import os.path
from prettytable import PrettyTable
import pyrax
import traceback

from pyraxshell.globals import INFO, WARNING, ERROR  # @UnusedWildImport @UnresolvedImport
from pyraxshell.plugins.libcloudfiles import LibCloudfiles  # @UnresolvedImport
from pyraxshell.utility import kv_dict_to_pretty_table, objects_to_pretty_table  # @UnresolvedImport
import pyraxshell.plugins.plugin


class Plugin(pyraxshell.plugins.plugin.Plugin, cmd.Cmd):
    '''
    pyrax shell POC - Manage CloudFiles module
    '''
    
    prompt = "RS cloudfiles>"    # default prompt

    def __init__(self):
        pyraxshell.plugins.plugin.Plugin.__init__(self)
        self.libplugin = LibCloudfiles()
        self.cf = pyrax.cloudfiles
    
    # ########################################
    # DEFAULT METHODS
    
#     def do_list(self, line):
#         '''
#         set default list method
#         '''
#         self.do_list_container(line)
    
    # ########################################
    # CONTAINER AND OBJECTS
    
    def do_create(self, line):
        '''
        create container
        
        @param container    name of the container
        '''
        if not len(self.varg) == 1:
            self.r(1, "please, specify container name", WARNING)
            return False
        self.cf.create_container(self.varg[0])
    
    def do_delete(self, line):
        '''
        download container or object
        
        Usage:
        
            delete container/object
            delete container recursive
        
        @param element    to delete
        @param recursive  recursive (WARNING: NO WAY TO RESTORE DELETED OBJECTS)
        '''
        retcode = 0
        if len(self.varg) == 0:
            retcode = 1
            retmsg = 'delete what?'
            self.r(0, retmsg, WARN)
            return False
        element = self.varg[0]
        if element.find('/') == -1:
            # delete container
            container_name = element
            try:
                container = self.cf.get_container(container_name)
                if len(self.varg) == 2 and self.varg[1] == 'recursive':
                    container.delete_all_objects()
                container.delete()
            except:
                tb = traceback.format_exc()
                self.r(1, tb, ERROR)
                return False
        else:
            # delete object
            (container_name, object_name) = self.varg[0].split('/', 1)
            try:
                object = self.cf.get_object(container_name, object_name)
                object.delete()
            except:
                tb = traceback.format_exc()
                self.r(1, tb, ERROR)
                return False
        
#         (container_name, object_name) = self.varg[0].split('/', 1)
#         dest_dir = self.varg[1]
#         if not os.path.isdir(dest_dir):
#             retmsg = 'destination directory \'%s\' does not exist' % dest_dir
#             self.r(1, retmsg, ERROR)
#             return False            
#         dest_dir = self.varg[1]
#         # select container
#         o = self.cf.get_object(container_name, object_name)
#         o.download(dest_dir)
#         self.r(0, '\'%s\' downloaded' % self.varg[0], INFO)     # everything's ok
        
    
    def complete_delete(self, text, line, begidx, endidx):
        # not auto-completing 'recursive' as it is dangerous
        params = []
        if len(self.varg) == 1:
            # autocomplete src
            pass
        elif len(self.varg) == 2:
            # autocomplete dest
            pass    
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_download(self, line):
        '''
        download object
        
        Usage:
        
            download container/virt/path/to/obj /local/dir
        
        @param src    source container/object
        @param dest   destination directory
        '''
        retcode = 0
        if len(self.varg) == 0:
            retcode = 1
            retmsg = 'src and dest missing'
        elif len(self.varg) == 1:
            retcode = 1
            retmsg = 'dest missing'
        if retcode == 1:
            self.r(0, retmsg, WARN)
            return False
        (container_name, object_name) = self.varg[0].split('/', 1)
        dest_dir = self.varg[1]
        if not os.path.isdir(dest_dir):
            retmsg = 'destination directory \'%s\' does not exist' % dest_dir
            self.r(1, retmsg, ERROR)
            return False            
        dest_dir = self.varg[1]
        # select container
        o = self.cf.get_object(container_name, object_name)
        o.download(dest_dir)
        self.r(0, '\'%s\' downloaded' % self.varg[0], INFO)     # everything's ok
        
    
    def complete_download(self, text, line, begidx, endidx):
#         params = ['src:', 'dst:']
        params = []
        if len(self.varg) == 1:
            # autocomplete src 'container/object'
            pass
        elif len(self.varg) == 2:
            # autocomplete dest
            print self.varg[1]
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
        list containers and objects
        
        Usage:
        
            list            -->    list containers
            list CONTAINER  -->    list objects within CONTAINER
        
        @param columns    if 'all' then all the properties displayed
        '''
        # check and set defaults
        retcode, retmsg = self.kvargcheck(
            {'name':'columns', 'default':''},
        )
        if not retcode:             # something bad happened
            self.r(1, retmsg, ERROR)
            return False
        
        if len(self.varg) >= 1:
            container_name = self.varg[0]
            container = self.cf.get_container(container_name)
            oo = container.get_objects(full_listing=True)
            props = ['name', 'content_type', 'etag', 'total_bytes']
            if len(oo):
                pt = objects_to_pretty_table(oo, props)
            else:
                self.r(0, "None", INFO)
                return True
        else:
            cc = self.cf.get_all_containers()
            # properties to be displayed
            props = ['name', 'object_count', 'total_bytes']
            if self.kvarg['columns'] == 'all':
                props = ['name', 'object_count', 'total_bytes',
                        'cdn_enabled', 'cdn_ios_uri', 'cdn_log_retention',
                        'cdn_ssl_uri', 'cdn_streaming_uri', 'cdn_ttl', 'cdn_uri',]
            # create a PrettyTable obj with those columns
            pt = objects_to_pretty_table(cc, props)
        # PrettyTable style
        pt.align['name'] = 'l' 
        for c in props[1:]:
            pt.align[c] = 'r'
        pt.sortby = 'name'
        #
#         print pt
        self.r(0, pt, INFO)
    
    def complete_list(self, text, line, begidx, endidx):
        params = ['columns:all']
#         print text
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    def do_make_public(self, line):
        '''
        make a container public
        
        Usage:
        
            make_public FOO [TTL]
            
        @param container    container name
        @param ttl          Time-To-Live (default: 900s)
        '''
        if not len(self.varg) == 1 and not len(self.varg) == 2:
            self.r(1, "Usage: make_public FOO [TTL]", WARNING)
            return False
        # set defaults
        (_name, _ttl) = (self.varg[0], 900)
        if len(self.varg) == 2:
            _ttl = self.varg[1]
        try:
            self.cf.make_container_public(_name, _ttl)
            self.r(0, 'ok', INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
    
    def do_make_private(self, line):
        '''
        make a container private
        
        Usage:
        
            make_private FOO
            
        @param container    container name
        '''
        if not len(self.varg) == 1:
            self.r(1, self.do_make_private.__doc__, WARNING)
            return False
        _name = self.varg[0]
        try:
            self.cf.make_container_private(_name)
            self.r(0, 'ok', INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)

    def do_upload(self, line):
        '''
        upload object
        
        Usage:
        
            upload /path/to/local/file container/virt/path/to/obj
        
        @param src    local file
        @param dest   source container/object
        '''
        retcode = 0
        if len(self.varg) == 0:
            retcode = 1
            retmsg = 'src and dest missing'
        elif len(self.varg) == 1:
            retcode = 1
            retmsg = 'dest missing'
        if retcode == 1:
            self.r(0, retmsg, WARN)
            return False
        (container_name, object_name) = self.varg[1].split('/', 1)
        local_filename = self.varg[0]
        if not os.path.isfile(local_filename):
            retmsg = 'local file \'%s\' does not exist' % local_filename
            self.r(1, retmsg, ERROR)
            return False
        # select container
        container = self.cf.get_container(container_name)
        container.upload_file(local_filename, object_name)
        # verify file checksum
        checksum_local = pyrax.utils.get_checksum(local_filename)
        checksum_remote = container.get_object(object_name).etag
        if checksum_local == checksum_remote:
            self.r(0, 'file uploaded successfully', INFO)
        else:
            self.r(1, 'error uploading file', ERROR)
    
    def complete_upload(self, text, line, begidx, endidx):
#         params = ['src:', 'dst:']
        params = []
        if len(self.varg) == 1:
            # autocomplete src
            pass
        elif len(self.varg) == 2:
            # autocomplete dest
            pass    
        if not text:
            completions = params[:]
        else:
            completions = [ f
                           for f in params
                            if f.startswith(text)
                            ]
        return completions
    
    # ########################################
    # METADATA
    
    def do_get_accout_metadata(self, line):
        '''
        overall usage for Cloud Files
        '''
        try:
            data = self.cf.get_account_metadata()
            pt = kv_dict_to_pretty_table(data)
            self.r(0, str(pt), INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False

    def do_set_account_metadata(self, line):
        '''
        set account metadata
        
        @param metadata_values  as 'key1:value1 .. keyn:valuen'
        '''
        try:
            self.cf.set_account_metadata(self.kvarg)
            cmd_out = "metadata set"
            self.r(0, cmd_out, INFO)
        except:
            tb = traceback.format_exc()
            self.r(1, tb, ERROR)
            return False
    
    
