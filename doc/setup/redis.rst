###########
Redis notes
###########


Introduction
============
This program extensively uses a runtime cache based on Redis.

Data durability
===============
To make this work best, you should enable data durability with your Redis instance.

    The append-only file is an alternative, fully durable strategy for Redis.
    It became available in version 1.1. You can turn on the AOF in your Redis
    configuration file (e.g. ``/etc/redis/redis.conf``)::

        appendonly yes

Running
=======
In order to run Redis from your local working tree, you might want to invoke::

    echo 'dir ./var/lib\nappendonly yes' | redis-server -

Looking glass
=============
In order to look into what is going on at the Redis substrate, you might want to invoke::

    redis-cli monitor

Please take care, the output is noisy.

Running in production
=====================
We experienced infrequent crashes of our Redis instance on CentOS Linux 7.6.1810.
In order to work around that problem, we configured systemd to restart the Redis
instance on failure by adding a file to the ``/etc`` directory as outlined below.

``cat /etc/systemd/system/redis.service.d/restart.conf``::

    [Service]
    # https://jonarcher.info/2015/08/ensure-systemd-services-restart-on-failure/
    # Please run "systemctl daemon-reload" after making changes to this file.
    Restart=always
    RestartSec=3

Please run ``systemctl daemon-reload`` after adding this file or making changes to it.

----

We have been tracking this issue at [1].

[1] https://github.com/earthobservations/luftdatenpumpe/issues/7
