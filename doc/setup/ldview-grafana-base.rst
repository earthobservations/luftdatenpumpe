.. highlight:: bash

########################
Luftdaten-Viewer Grafana
########################

This walkthrough brings everything in place to visualize the data feed of
`Sensor.Community`_, formerly ``luftdaten.info``, using `Grafana`_.


************
Installation
************


Flux datasource
===============

Flux datasource::

    grafana-cli plugins install grafana-influxdb-flux-datasource


Panodata Map Panel
==================
The map component for Grafana used within this setup is the `Panodata Map Panel`_.

Because it is not a built-in plugin, and not available on the `Grafana plugin catalog`_,
it is not signed. To allow using unsigned plugins starting with Grafana 7.x, please use
the `allow_loading_unsigned_plugins`_ configuration setting, which is located within
the ``[plugins]`` section of ``/etc/grafana/grafana.ini``.

.. code-block:: ini

    allow_loading_unsigned_plugins = panodata-map-panel

Install `Panodata Map Panel`_::

    grafana-cli \
        --pluginUrl https://github.com/panodata/panodata-map-panel/releases/download/0.16.0/panodata-map-panel-0.16.0.zip \
        plugins install panodata-map-panel

Finally, restart your Grafana instance::

    systemctl restart grafana-server

.. warning::

    Please note this procedure has been confirmed to work with Grafana versions up
    to Grafana 8.x. It has not been verified on the most recent Grafana 9.x version.


************
LDI Metadata
************


Storage for station list
========================

The Panodata Map Panel (ex. Grafana Worldmap Panel) requires a JSON file
``ldi-stations.json`` to display appropriate popup labels to each data point
on the map.

This section of the documentation describes how to create the
corresponding file using ``luftdatenpumpe`` in a way it can be
picked up by the map panel through HTTP.

Create directory for stations file::

    mkdir -p /var/lib/grafana/data/json
    chown -R grafana:grafana /var/lib/grafana/data
    ln -sf /var/lib/grafana/data /usr/share/grafana/public/

Let all processing happen on network "LDI"::

    export LDP_NETWORK=ldi

Define stations file::

    stationsfile=/var/lib/grafana/data/json/ldi-stations.json

.. note::

    On a macOS/Homebrew system, Grafana is installed to ``/usr/local/share/grafana`` and ``/usr/local/var/lib/grafana``.
    You might have to adjust the ``$stationsfile`` path to the environment you are running this program on::

        mkdir -p /usr/local/var/lib/grafana/data/json
        ln -sf /usr/local/var/lib/grafana/data /usr/local/share/grafana/public/

        stationsfile=/usr/local/var/lib/grafana/data/json/ldi-stations.json


Create station list
===================
Write stations and metadata to RDBMS database (PostgreSQL)::

    # Acquire baseline from live API.
    luftdatenpumpe stations --reverse-geocode \
        --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

    # Optionally acquire more stations from CSV archive files.
    luftdatenpumpe stations --reverse-geocode \
        --source=file:///var/spool/archive.luftdaten.info \
        --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

Create RDBMS database view ``ldi_network``::

    # This is important to do *after* importing the metadata, as the
    # previous steps will properly populate the database on the first hand.
    luftdatenpumpe database \
        --target=postgresql://luftdatenpumpe@localhost/weatherbase --create-views --grant-user=grafana

Export station metadata from RDBMS database (PostgreSQL) to JSON file for Panodata Map Panel::

    luftdatenpumpe stations \
        --source=postgresql://luftdatenpumpe@localhost/weatherbase \
        --target=json.flex+stream://sys.stdout \
        --target-fieldmap='key=station_id|str,name=road_and_name_and_id' > $stationsfile

Check::

    export GRAFANA_URL=http://localhost:3000
    http $GRAFANA_URL/public/data/json/ldi-stations.json | jq length
    760


*********************
LDI Grafana artefacts
*********************

Prerequisites
=============
::

    # Define the URL to your Grafana instance.
    # This saves you from having to supply it all over again to the subsequent commands.
    export GRAFANA_URL=http://localhost:3000

    # Sign in to your Grafana instance once.
    # This saves you from having to supply "--auth=admin:admin" on every subsequent invocation.
    http --session=grafana $GRAFANA_URL --auth=admin:admin


.. note::

    When running on localhost, use this URL instead::

        export GRAFANA_URL=http://localhost:3000

Datasources
===========
::

    # Create data source object for "weatherbase @ PostgreSQL".
    luftdatenpumpe grafana --kind=datasource --name=weatherbase \
        | http --session=grafana POST $GRAFANA_URL/api/datasources

    # Create data source object for "luftdaten_info @ InfluxDB".
    luftdatenpumpe grafana --kind=datasource --name=influxdb \
        --variables=tsdbDatasource=luftdaten_info \
        | http --session=grafana POST $GRAFANA_URL/api/datasources

.. note::

    Before being able to create the data source objects again, you will have to delete them first::

        http --session=grafana DELETE $GRAFANA_URL/api/datasources/name/weatherbase
        http --session=grafana DELETE $GRAFANA_URL/api/datasources/name/luftdaten_info


Dashboards
==========
Create dashboard with graph panel::

    luftdatenpumpe grafana --kind=dashboard --name=trend \
        --variables=tsdbDatasource=luftdaten_info,sensorNetwork=ldi \
        --fields=pm2-5=P2,pm10=P1 \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db

Create dashboard with map and table panels::

    luftdatenpumpe grafana --kind=dashboard --name=map \
        --variables=tsdbDatasource=luftdaten_info,sensorNetwork=ldi,jsonUrl=/public/data/json/ldi-stations.json,autoPanLabels=false \
        --fields=pm2-5=P2,pm10=P1 \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db

.. note:: This references the station list JSON file created in one of the previous steps.


.. _allow_loading_unsigned_plugins: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#allow_loading_unsigned_plugins
.. _Grafana: https://grafana.com/
.. _Grafana plugin catalog: https://grafana.com/grafana/plugins/
.. _luftdaten.info: https://luftdaten.info
.. _Panodata Map Panel: https://community.panodata.org/t/panodata-map-panel-for-grafana/121
.. _Sensor.Community: https://sensor.community/en/
