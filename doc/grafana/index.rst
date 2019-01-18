###################
Grafana integration
###################


******************************
LDI on Grafana Worldmap Plugin
******************************

Setup
=====
::

    git clone https://github.com/hiveeyes/grafana-worldmap-panel
    git checkout table-plus-json
    npm install
    npm run build

Linux::

    ln -s /opt/grafana-worldmap-panel /var/lib/grafana/plugins/

Mac OS X / Homebrew::

    ln -s ~/develop/grafana-worldmap-panel /usr/local/var/lib/grafana/plugins/

Start Grafana::

    make grafana-start



Configure
=========


JSON files
----------
Create ldi-stations.json (Homebrew)::

    stationsfile=/usr/local/share/grafana/public/json/ldi-stations.json
    mkdir -p $(dirname $stationsfile)

    # Write list of stations and metadata from live API to RDBMS database (PostgreSQL)
    luftdatenpumpe stations --reverse-geocode --target=postgresql:///weatherbase --progress

    # Optionally add more stations from CSV archive files
    luftdatenpumpe stations --reverse-geocode --source=file:///var/spool/archive.luftdaten.info --target=postgresql:///weatherbase --progress

    # Create database view
    luftdatenpumpe stations --target=postgresql:///weatherbase --create-database-view

    # Read station information from RDBMS database (PostgreSQL) and format for Grafana Worldmap Panel
    luftdatenpumpe stations --source=postgresql:///weatherbase --target=json.grafana.kn+stream://sys.stdout > $stationsfile


Datasources
-----------
::

    # InfluxDB datasource "luftdaten_info"
    http POST http://localhost:3000/api/datasources @doc/grafana/ldi/datasource-influxdb.json --auth=admin:admin

    # PostgreSQL datasource "weatherbase"
    http POST http://localhost:3000/api/datasources @doc/grafana/ldi/datasource-postgresql.json --auth=admin:admin


Dashboard
---------
::

    # Dashboard with Graph Panel. Filter by location and sensor type.
    http POST http://localhost:3000/api/dashboards/db @doc/grafana/ldi/dashboard-trend.json --auth=admin:admin

    # Dashboard with Worldmap Panel. Filter by location and sensor type.
    http POST http://localhost:3000/api/dashboards/db @doc/grafana/ldi/dashboard-map.json --auth=admin:admin

.. todo:: Insert screenshots here.
