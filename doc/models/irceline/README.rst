################################
Data models for IRCELINE network
################################


********
Upstream
********

Stations
========
::

    # Stations
    http 'http://geo.irceline.be/sos/api/v1/stations?expanded=true' | jq '[ .[] | select(.properties.id==1234 or .properties.id==1720) ]' > upstream-stations.json

Readings
========
::

    # Readings
    http POST http://geo.irceline.be/sos/api/v1/timeseries/getData timeseries:='[10744,7185]' timespan='PT3h/2019-04-24T01:00:00Z' | jq . > upstream-timeseries.json


**********
Downstream
**********
Running Luftdatenpumpe without reverse geocoding yields compact output,
while enabling geocoding will enrich the station information significantly.

Stations
========
::

    # No reverse geocoding.
    luftdatenpumpe stations --network=irceline --station=1234,1720 > stations-compact.json

    # With reverse geocoding.
    luftdatenpumpe stations --network=irceline --station=1234,1720 --reverse-geocode > stations-geocoded.json


Readings
========
::

    # No reverse geocoding.
    luftdatenpumpe readings --network=irceline --station=1234,1720 > readings-compact.json

    # With reverse geocoding.
    luftdatenpumpe readings --network=irceline --station=1234,1720 --reverse-geocode > readings-geocoded.json
