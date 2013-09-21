pyraxshell
==========

CLI tool and interpreter to manage
`OpenStack <http://www.openstack.org/>`__ and
`Rackspace <http://www.rackspace.com/>`__ Cloud products. It leverages
`pyrax <https://github.com/rackspace/pyrax>`__ module, therefore it aims
to expose all the features implemented in *pyrax*.

Watch *pyraxshell* in action:

**ATTENTION** *pyraxshell* is currently in development stage, therefore
it should be used for testing purposes only.

Installation
------------

From sources
~~~~~~~~~~~~

Just clone the `pyraxshell
repository <https://github.com/siso/pyraxshell>`__ on
`Github <https://github.com/>`__ and run it:

::

    $ git clone https://github.com/siso/pyraxshell
    $ cd pyraxshell
    $ python pyraxshell

Authentication
--------------

*pyraxshell* supports three different authentication methods:
credentials file, login and token.

Credentials file
~~~~~~~~~~~~~~~~

Create ``~/.pyrax.cfg`` file with your credentials:

::

    cat > ~/.pyrax.cfg << EOF
    [rackspace_cloud]
    identity_type=rackspace
    username = USERNAME
    api_key = APIKEY
    region = REGION
    EOF

then simply run ``python pyraxshell`` and *pyraxshell* will try to
authenticate with *~/.pyrax.cfg* credentials.

Login
~~~~~

Run *pyraxshell* and enter login credentials:

::

    $ python pyraxshell
    H>auth
    H auth>login identity_type:rackspace username:USERNAME apikey:APIKEY region=REGION

Token
~~~~~

Run *pyraxshell* and enter your token:

::

    $ python pyraxshell
    H>auth
    H auth>token token:TOKEN tenantId:TENANTID identity_type:IDENTITYTYPE region:REGION

Quickstart
----------

Using pyraxshell interactively
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*pyraxshell* can be executed **interactively**, so you can start
experimenting `OpenStack <http://www.openstack.org/>`__ and
`Rackspace <http://www.rackspace.com/>`__ with few simple commands:

::

    $ python pyraxshell
    H>

hit ``TAB-TAB`` to auto-complete:

::

    H>
    EOF        auth       databases  endpoints  help       servers    test
    H>auth
    EOF               credentials       is_authenticated  print_identity    token
    change_password   help              login             print_token

authenticate:

::

    H auth>login identity_type:rackspace username:MYUSERNAME apikey:MYAPIKEY region=LON

return to the previous menu/interpreter ``CTRL-D``:

::

    H auth>
    H>servers
    H servers>
    EOF           delete        help          list_flavors  
    create        details       list          list_images   
    H servers>list_flavors
    +----+-------------------------+-------+------+-------+
    | id |           name          |  ram  | swap | vcpus |
    +----+-------------------------+-------+------+-------+
    | 2  | 512MB Standard Instance |  512  | 512  |   1   |
    ...

and so on, you have got the idea. No need to learn anything new, just
use it as you would do with any other interpreter, with history,
auto-completion, *etc*.

Default values
^^^^^^^^^^^^^^

If a parameter has a default value, then it is considered optional:

::

    H dns>help create_domain

            create a domain
            
            Parameters:
            
            name               name of the domain
            email_address    
            ttl                TTL (optional, default:900)
            comment            (optional, default:void)

Using pyraxshell non-interactively with pyraxcli
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pyraxcli`` is a wrapper which allows to run *pyraxshell* commands from
the command-line, e.g.:

``$ python pyraxshell/pyraxcli.py servers, list, EOF, loadbalancers, list, list_nodes id:81957``

using the same *pyraxshell syntax*, and commands separated by *commas*.

Using pyraxshell non-interactively
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running *pyraxshell* **non-teractively** is pretty easy, and it is the
best way to automate tasks. Just create a text file with the commands
you want to run:

::

    $ cat > commands.txt << EOF
    auth
    login identity_type:rackspace username:MYUSERNAME apikey:MYAPIKEY region=LON
    exit
    servers
    list_flavors
    EOF

and *pipe* that to standard input:

::

    $ cat commands.txt | python pyraxshell
    ...
    +----+-------------------------+-------+------+-------+
    | id |           name          |  ram  | swap | vcpus |
    +----+-------------------------+-------+------+-------+
    | 2  | 512MB Standard Instance |  512  | 512  |   1   |
    ...

To use *comments* start a line with '#', then run:

``$ cat commands.txt | grep -v "^#" | python pyraxshell``

i.e.:

::

    $ cat > commands.txt << EOF
    # THIS IS A COMMENT
    # AUTHENTICATE
    auth
    login identity_type:rackspace username:MYUSERNAME apikey:MYAPIKEY region=LON
    # EXIT AUTHENTICATION SUB-INTERPRETER
    exit
    # ENTER SERVERS MENU
    servers
    # LIST FLAVORS
    list_flavors
    EOF

See ``./scripts`` directory which contains some examples.

Features
--------

*pyraxshell* leverages its *plugins system* to provide users with all
its features. Please, read ``PLUGINS.md`` to know more about the
*pyraxshell plug-ins system*, and feel free to poke around
``./pyraxshell/plugins`` directory too!

Logging
-------

*Logging* to *stdout* and to file ``/tmp/pyraxshell.log`` is enabled by
default. It can be configured according to your needs, just edit
``./conf/logging.conf``, and refer to `Logging facility for
Python <http://docs.python.org/2/library/logging.html>`__.

Roadmap
-------

What features will be added to *pyraxshell*? See ``ROADMAP.md``.

Issues, features and questions
------------------------------

Please, consult `pyraxshell
issues <https://github.com/siso/pyraxshell/issues/new>`__, raise a new
ticket, and tag it accordingly.

License
-------

GPL version 3, see ``LICENSE``.
