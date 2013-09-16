pyraxshell - Plug-ins system
======

[pyraxshell](https://github.com/siso/pyraxshell) should be extended via plug-ins:

* placed in ```./pyraxshell/plugins```
* named ```plugin_XXX.py```
* import a relate ```libXXX.py``` library which provides required functionalities
* see ```./pyraxshell/plugins/plugin_test.py``` to understando how to write a plugin


## Reloading plug-ins
Plug-ins can be reloaded from the *main* interpreter:

```
H>
EOF             credits         dns             help            list_plugins    reload_plugins  services        unload_plugins  
auth            databases       exit            license         loadbalancers   servers         test            version         
H>unload_plugins
unloading plug-ins (INFO)
plugin 'do_dns' unloaded (INFO)
plugin 'do_loadbalancers' unloaded (INFO)
plugin 'do_auth' unloaded (INFO)
plugin 'do_servers' unloaded (INFO)
plugin 'do_test' unloaded (INFO)
plugin 'do_databases' unloaded (INFO)
plugin 'do_services' unloaded (INFO)
H>
EOF             credits         exit            help            license         list_plugins    reload_plugins  unload_plugins  version         
H>reload_plugins
unloading plug-ins (INFO)
plug-ins loaded: auth, databases, dns, loadbalancers, servers, services, test (INFO)
H>
EOF             credits         dns             help            list_plugins    reload_plugins  services        unload_plugins  
auth            databases       exit            license         loadbalancers   servers         test            version         
H>
```

That allows developer to speed new plug-ins developing process up, as quitting and restarting *pyraxshell* is not required.
 
