.. highlight:: bash

################################
Luftdaten-Viewer Grafana for VMM
################################

This walkthrough builds upon the baseline documentation about setting up
Luftdatenpumpe with `Grafana`_, and is a guideline for `VMM`_ to visualize the
data feed of `IRCELINE`_.


*****
Setup
*****

Let all processing happen on network "IRCELINE"::

    export LDP_NETWORK=irceline

LDI network
===========
Create dashboard with map and table panels for LDI Belgium::

    luftdatenpumpe grafana --kind=dashboard --name=map \
        --variables=tsdbDatasource=luftdaten_info,sensorNetwork=ldi,mapCenterLatitude=50.82502,mapCenterLongitude=4.46045,initialZoom=7,jsonUrl=/public/data/json/ldi-stations.json,autoPanLabels=false \
        --fields=pm2-5=P2,pm10=P1 \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db


IRCELINE network
================
::

    # Define Grafana instance and login.
    export GRAFANA_URL=http://localhost:3000
    http --session=grafana $GRAFANA_URL --auth=admin:admin


Create datasource::

    # Create data source object for "vmm @ InfluxDB".
    luftdatenpumpe grafana --kind=datasource --name=influxdb \
        --variables=tsdbDatasource=vmm \
        | http --session=grafana POST $GRAFANA_URL/api/datasources

Create dashboard with graph panel::

    luftdatenpumpe grafana --kind=dashboard --name=trend \
        --variables=tsdbDatasource=vmm,sensorNetwork=irceline,timeRefresh=1h \
        --fields=pm1=particulate-matter-1-m,pm2-5=particulate-matter-2-5-m,pm10=particulate-matter-10-m \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db

Export station metadata from RDBMS database (PostgreSQL) to JSON file for Panodata Map Panel::

    stationsfile=/var/lib/grafana/data/json/vmm-stations.json
    # macOS: stationsfile=/usr/local/var/lib/grafana/data/json/vmm-stations.json

    luftdatenpumpe stations --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.flex+stream://sys.stdout --target-fieldmap='key=station_id|str,name=sos_feature_and_id' > $stationsfile

Create dashboard with map and table panels for IRCELINE::

    luftdatenpumpe grafana --kind=dashboard --name=map \
        --variables=tsdbDatasource=vmm,sensorNetwork=irceline,timeFromOffset=120m,timeRefresh=1h,mapCenterLatitude=50.82502,mapCenterLongitude=4.46045,initialZoom=7,jsonUrl=/public/data/json/vmm-stations.json,autoPanLabels=false \
        --fields=pm1=particulate-matter-1-m,pm2-5=particulate-matter-2-5-m,pm10=particulate-matter-10-m \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db


.. _Grafana: https://grafana.com/
.. _IRCELINE: https://www.irceline.be/en
.. _VMM: https://www.vmm.be/
