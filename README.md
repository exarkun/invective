invective
=========

invective is a chat client with a terminal interface.  It is written in Python
using Twisted.

installation
============

Installation is not yet supported.  Set PYTHONPATH and run bin/invect from the
source checkout.

features
========

invective is not yet usable in practice to replace your current chat client.  It
supports only IRC, and only a few minimal interactions.  You can give it a try
using the "/server" command once invective is running, but don't expect a lot
yet (another command you'll find useful is "/quit").

plans
=====

The purpose of invective is to replace the nasty old fashioned
terminal-interface clients with badly broken networking code or bad user
interfaces.  Near term development will focus on building a solid networking
layer and a good user interface, rather than adding support for a billion
different chat networks.

unit tests
==========

invective uses xUnit-style automated testing.  You can run its tests using
trial:

    $ trial invective

contributing
============

Feel free to contribute features and bug fixes.  Please file an issue on github
describing the feature you're adding or bug you're fixing (preferably before you
do the work, so there's time to discuss whether it makes sense or how to
approach it), then send a pull request when you're ready.
