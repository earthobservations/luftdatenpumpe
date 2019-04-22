#############################
Luftdaten-Viewer Applications
#############################

**********
Foundation
**********

Configure package repository
============================
Hiveeyes is hosting recent releases of InfluxDB and Grafana there.
We are mostly also running exactly these releases on our production servers.

Add Hiveeyes package repository::

    wget -qO - https://packages.hiveeyes.org/hiveeyes/foss/debian/pubkey.txt | apt-key add -

Add Hiveeyes package repository, e.g. by appending this to ``/etc/apt/sources.list``::

    deb https://packages.hiveeyes.org/hiveeyes/foss/debian/ testing main foundation

Reindex package database::

    apt install apt-transport-https
    apt update


Install packages
================

Debian
------
::

    apt install influxdb postgis redis-server redis-tools grafana

CentOS
------
::

    rpm -Uvh https://download.postgresql.org/pub/repos/yum/11/redhat/rhel-7-x86_64/pgdg-centos11-11-2.noarch.rpm
    yum -y install postgresql11-server postgis2_11


macOS/Homebrew
--------------
::

    brew install influxdb postgis redis grafana


Configure Redis
===============
This program extensively uses a runtime cache based on Redis.
To make this work best, you should enable data durability with your Redis instance.

    The append-only file is an alternative, fully-durable strategy for Redis. It became available in version 1.1.
    You can turn on the AOF in your Redis configuration file (e.g. `/etc/redis/redis.conf`)::

        appendonly yes
