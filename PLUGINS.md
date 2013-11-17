pyraxshell - Plug-ins system
======

[pyraxshell](https://github.com/siso/pyraxshell) should be extended via plug-ins:

* placed in ```./pyraxshell/plugins```
* named ```plugin_XXX.py```
* ```plugin_XXX.py``` inherits ```pyraxshell.plugins.plugin.Plugin```
* leverage ```libXXX.py``` library which implements logic
* ```libXXX.py``` inherits ```pyraxshell.plugins.lib.Lib```

See ```./pyraxshell/plugins/plugin_test.py``` and see how to write a plugin
