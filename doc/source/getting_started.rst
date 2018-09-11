.. _getting_started:

Getting started
===============

How to import the cinf_database
-------------------------------

The cinf_database module is a single file module. This means that to
be able to use it, can be as simple as dropping the file in the same
folder as your data treatment code files.

Alternatively, the module can also be placed somewhere in your
PYTHONPATH to make it accessible from anywhere, without having to have
copies. More about that in the following section.


Adding cinf_database to PYTHONPATH
----------------------------------

TODO


Using the cinf_database module from outside DTU
-----------------------------------------------

The cinf_database module should work with the DTU VPN. You can read
more about `how to install here
<https://wiki.fysik.dtu.dk/it/VPN%20connection%20to%20DTU>`_ and do
`the actual download and install from here <vpn.ait.dtu.dk>`_.

Alternatively, and the way it used to be done, if you cannot make the
DTU VPN work or do not wish to use it, you can set up a port forward
between a local port and the MySQL database. The module will
automatically look for a port forward on port 9999.
