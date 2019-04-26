######################################
Data models for luftdaten.info network
######################################


********
Upstream
********
::

    http https://api.luftdaten.info/static/v1/data.json | jq '[ .[] | select(.location.id==28 or .location.id==1071) ]' > upstream.json


**********
Downstream
**********
Running Luftdatenpumpe without reverse geocoding yields compact output,
while enabling geocoding will enrich the station information significantly.

Stations
========
::

    # No reverse geocoding.
    luftdatenpumpe stations --network=ldi --station=28,1071 > stations-compact.json

    # With reverse geocoding.
    luftdatenpumpe stations --network=ldi --station=28,1071 --reverse-geocode > stations-geocoded.json


Readings
========
::

    # No reverse geocoding.
    luftdatenpumpe readings --network=ldi --station=28,1071 > readings-compact.json

::

    # With reverse geocoding.
    luftdatenpumpe readings --network=ldi --station=28,1071 --reverse-geocode > readings-geocoded.json
