#############################
Luftdaten-Viewer Applications
#############################


*******
Install
*******
- `Luftdaten-Viewer Applications for Debian`_
- `Luftdaten-Viewer Applications for CentOS`_
- `Luftdaten-Viewer Applications for macOS`_

.. _Luftdaten-Viewer Applications for Debian: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/setup/ldview-applications-debian.rst
.. _Luftdaten-Viewer Applications for CentOS: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/setup/ldview-applications-centos.rst
.. _Luftdaten-Viewer Applications for macOS: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/setup/ldview-applications-macos.rst


Configure Redis
===============
This program extensively uses a runtime cache based on Redis.
To make this work best, you should enable data durability with your Redis instance.

    The append-only file is an alternative, fully-durable strategy for Redis. It became available in version 1.1.
    You can turn on the AOF in your Redis configuration file (e.g. `/etc/redis/redis.conf`)::

        appendonly yes
