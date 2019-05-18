########################
Luftdaten-Viewer Grafana
########################

This brings everything in place to visualize
the data feed of luftdaten.info using Grafana.


************
Installation
************

Install Grafana Plugins
=======================

Flux datasource::

    grafana-cli plugins install grafana-influxdb-flux-datasource

Worldmap Panel 0.3.0-dev::

    grafana-cli --pluginUrl https://github.com/hiveeyes/grafana-worldmap-panel/archive/0.3.0-dev2.zip plugins install grafana-worldmap-panel
    systemctl restart grafana-server

See also https://community.hiveeyes.org/t/grafana-worldmap-panel-0-3-0-dev-series/1824.


************
LDI Metadata
************


Storage for station list
========================
The Grafana Worldmap Panel requires a JSON file ``ldi-stations.json`` to
display appropriate popup labels to each data point on the map.

This section of the documentation describes how to create the
corresponding file using ``luftdatenpumpe`` in a way it can be
picked up by the Grafana Worldmap Panel through HTTP.

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
    luftdatenpumpe stations --reverse-geocode --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

    # Optionally acquire more stations from CSV archive files.
    luftdatenpumpe stations --reverse-geocode --source=file:///var/spool/archive.luftdaten.info --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

Create RDBMS database view ``ldi_network``::

    # This is important to do *after* importing the metadata, as the
    # previous steps will properly populate the database on the first hand.
    luftdatenpumpe database --target=postgresql://luftdatenpumpe@localhost/weatherbase --create-views --grant-user=grafana

Create station list file for Grafana Worldmap Panel from RDBMS database (PostgreSQL)::

    luftdatenpumpe stations --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.grafana.kn+stream://sys.stdout > $stationsfile

Check::

    export GRAFANA_URL=https://daq.example.org/grafana
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
    export GRAFANA_URL=https://daq.example.org/grafana

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

Create dashboard with worldmap and table panels::

    luftdatenpumpe grafana --kind=dashboard --name=map \
        --variables=tsdbDatasource=luftdaten_info,sensorNetwork=ldi,jsonUrl=/public/data/json/ldi-stations.json,autoPanLabels=false \
        --fields=pm2-5=P2,pm10=P1 \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db

.. note:: This references the station list JSON file created in one of the previous steps.
