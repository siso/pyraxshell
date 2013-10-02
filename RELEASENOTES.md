Release notes for pyraxshell
=======

## 2013.XX.XX - Version 0.2.5
  * Added logging to file/db feature
  * Lib/Plugin_Auth logs to file/db

## 2013.09.29 - Version 0.2.4
  * Added SIGINT/SIGTERM handler to stop threads gracefully
  * Added Notifier (a threaded message queue system)
  * Implemented long lasting operation use Notifier 

## 2013.09.28 - Version 0.2.3
  * Fixed issue #11
  * Fixed issue #9
  * Added SQLite3 support
  * Added '~/.pyraxshell' directory and config files support
  * Fixed issue #14
  * Added sessions support
  * Added 'r' (record) function to log messages to file and sessions to db
  * Fixed non-interactive command output
  * Implemented main and loggin configuration files support

## 2013.09.22 - Version 0.2.2
  * Fixed issue #3
  * Improved 'plugins.libdns'
  * Started writing unit-tests 

## 2013.09.21 - Version 0.2.1
  * Fixed issue #7 - Remove "unload_plugins"
  * Fixed 'import' in 'pyraxshell::load_plugins()'
  * Fixed issue #6
  * Fixed issue #10

## 2013.09.16 - Version 0.2.0
  * Added features to plugin_loadbalancers
  * Added features to plugin_services
  * Added features to plugin_servers

## 2013.09.15 - Version 0.1.9
  * Minor fixes
  * Fixed plugin_dns methods
  
## 2013.09.14 - Version 0.1.8
  * Fixed issue #1
  * Added base Plugin class

## 2013.09.07 - Version 0.1.1
  * Added plugin_service
  * Added support for Cloud Servers Snapshots
  * Added feature for changing root password of Cloud Servers
  * Added feature for rebooting Cloud Servers
