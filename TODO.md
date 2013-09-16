pyraxshell - TO-DO list
======

* command output should be: [RETURN_CODE][INFO][ERROR_LEVEL] (i.e.: '[0][all good!][INFO]'  
* i.e.: server name:a<TAB>... <== suggest servers whose name starts with 'a'
* see alternatives to cmd in the Cheese Shop - CmdLoop, cly, CMdO, and pycopia. cly, cmd2 to support
  searchable history, colors, ...
* all 'complete_XXX' methods are almost the same
* code can be optimised (get rid of repetition (focus on adding features until v0.2))
* log messages should report at least class and method names
* support comments, mainly useful in non-interactive mode
* implement 'wait_for_completion' option for long lasting operations (create db instance, server, ...)

## Plug-ins

### Cloud databases

* create_instance does not notify of progress and completion
* list_instances should list instance_index (harmful, instances might be created between 'list_instances' and 'create_database instance_index:X' invocation
* list_database should accept instance_name as param
* list_database should accept instance_index as param
* create_database should accept instance_index as param
* resize_instance: rename 'id' to 'instance_id' for consitency
* delete_instance: rename 'id' to 'instance_id' for consitency

## Cloud DNS

...

## Cloud Load-balancers

...

## Cloud Servers

...

## Services

...

