#####################################
Luftdaten-Viewer Grafana for IRCELINE
#####################################

This brings everything in place to visualize
the data feed of IRCELINE using Grafana.


*****
Setup
*****
Create datasource and graph dashboard::

    # Define Grafana instance and login.
    export GRAFANA_URL=https://daq.example.org/grafana
    http --session=grafana $GRAFANA_URL --auth=admin:admin

    # Create data source object for "vmm @ InfluxDB".
    luftdatenpumpe grafana --kind=datasource --name=influxdb \
        --variables=tsdbDatasource=vmm \
        | http --session=grafana POST $GRAFANA_URL/api/datasources

    luftdatenpumpe grafana --kind=dashboard --name=trend \
        --variables=tsdbDatasource=vmm,sensorNetwork=irceline,timeFromOffset=120m,timeRefresh=1h \
        --fields=pm1=particulate-matter-1-m,pm2-5=particulate-matter-2-5-m,pm10=particulate-matter-10-m \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db

Create station list file for Grafana Worldmap Panel from RDBMS database (PostgreSQL)::

    stationsfile=/usr/local/var/lib/grafana/data/json/irceline-stations.json
    luftdatenpumpe stations --network=irceline --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.grafana.kn+stream://sys.stdout > $stationsfile

Create Worldmap Panel::

    luftdatenpumpe grafana --kind=dashboard --name=map \
        --variables=tsdbDatasource=vmm,sensorNetwork=irceline,timeFromOffset=120m,timeRefresh=1h,mapCenterLatitude=50.82502,mapCenterLongitude=4.46045,initialZoom=7,jsonUrl=/public/data/json/irceline-stations.json,autoPanLabels=false \
        --fields=pm1=particulate-matter-1-m,pm2-5=particulate-matter-2-5-m,pm10=particulate-matter-10-m \
        | http --session=grafana POST $GRAFANA_URL/api/dashboards/db
