#######################################
Integrating Luftdatenpumpe with Grafana
#######################################


************
Installation
************

Setup Grafana worldmap panel
============================
::

    git clone https://github.com/hiveeyes/grafana-worldmap-panel
    git checkout table-plus-json
    npm install
    npm run build

Linux::

    ln -s /opt/grafana-worldmap-panel /var/lib/grafana/plugins/
    systemctl restart grafana-server

Mac OS X / Homebrew::

    ln -s ~/develop/grafana-worldmap-panel /usr/local/var/lib/grafana/plugins/
    make grafana-start


*******************
LDI metadata import
*******************
This brings everything in place to visualize
datasets from luftdaten.info fame in Grafana.


Station list
============
Create station list file ``ldi-stations.json`` for Grafana Worldmap Panel.

Define stations file::

    stationsfile=/usr/local/share/grafana/public/json/ldi-stations.json
    mkdir -p $(dirname $stationsfile)

Write stations and metadata to RDBMS database (PostgreSQL)::

    # Acquire baseline from live API.
    luftdatenpumpe stations --reverse-geocode --target=postgresql:///weatherbase --progress

    # Optionally acquire more stations from CSV archive files.
    luftdatenpumpe stations --reverse-geocode --source=file:///var/spool/archive.luftdaten.info --target=postgresql:///weatherbase --progress

Create RDBMS database view ``ldi_network``::

    # This is important to do *after* importing the metadata, as the
    # previous steps will properly populate the database on the first hand.
    luftdatenpumpe stations --target=postgresql:///weatherbase --create-database-view

Create station list file for Grafana Worldmap Panel from RDBMS database (PostgreSQL)::

    luftdatenpumpe stations --source=postgresql:///weatherbase --target=json.grafana.kn+stream://sys.stdout > $stationsfile


.. note::

    On this system (macOS/Homebrew), Grafana is installed to ``/usr/local/share/grafana``.
    You might have to adjust this to the environment you are running this program on.


*********************
LDI Grafana artefacts
*********************

Prerequisites
=============
::

    # Sign in to your Grafana instance once.
    # This saves you from having to supply "--auth=admin:admin" on every subsequent invocation.
    http --session=grafana http://localhost:3000/ --auth=admin:admin


Datasources
===========
::

    # Create data source object for "luftdaten_info @ InfluxDB".
    luftdatenpumpe grafana --kind=datasource --name=luftdaten_info | \
        http --session=grafana POST http://localhost:3000/api/datasources

    # Create data source object for "weatherbase @ PostgreSQL".
    luftdatenpumpe grafana --kind=datasource --name=weatherbase | \
        http --session=grafana POST http://localhost:3000/api/datasources


.. note::

    Before being able to create the data source objects again, you will have to delete them first::

        http --session=grafana DELETE http://localhost:3000/api/datasources/name/luftdaten_info
        http --session=grafana DELETE http://localhost:3000/api/datasources/name/weatherbase


Dashboards
==========
Create dashboard with graph panel::

    luftdatenpumpe grafana --kind=dashboard --name=trend | \
        http --session=grafana POST http://localhost:3000/api/dashboards/db

Create dashboard with worldmap and table panels::

    luftdatenpumpe grafana --kind=dashboard --name=map --variables=jsonUrl=/public/json/ldi-stations.json | \
        http --session=grafana POST http://localhost:3000/api/dashboards/db

.. note:: This references the station list JSON file created in one of the previous steps.


.. todo:: Insert more detailed screenshots here.
