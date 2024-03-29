.. highlight:: bash

#############################
Luftdaten-Viewer Applications
#############################

This section of the documentation outlines how to install the prerequisites
for a full system based on Luftdatenpumpe. It is Grafana, InfluxDB, PostGIS,
and Redis.

.. tabs::

    .. tab:: Debian

        **Configure package repository**

        Hiveeyes is hosting recent releases of InfluxDB and Grafana there.
        We are mostly also running exactly these releases on our production servers.

        Add Hiveeyes package repository::

            wget -qO - https://packages.hiveeyes.org/hiveeyes/foss/debian/pubkey.txt | apt-key add -

        Add Hiveeyes package repository, e.g. by appending this to ``/etc/apt/sources.list``::

            deb https://packages.hiveeyes.org/hiveeyes/foss/debian/ testing main foundation

        Reindex package database::

            apt install apt-transport-https
            apt update


        **Install packages**
        ::

            apt install influxdb postgis redis-server redis-tools grafana


    .. tab:: CentOS

        .. todo:: Transfer from ``belgiumAir/installation.rst``.

    .. tab:: macOS

        ::

            brew install grafana influxdb postgis redis

