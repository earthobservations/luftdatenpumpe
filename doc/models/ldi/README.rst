######################################
Data models for luftdaten.info network
######################################


*******************
API and data schema
*******************

Please have a look at the upstream documentation first:

- https://github.com/opendata-stuttgart/meta/wiki/APIs
- https://github.com/opendata-stuttgart/meta/wiki/EN-APIs

:doc:`schema` has more information and example documents about LDI's
official data schema in JSON format.


********
Upstream
********
::

    http https://api.luftdaten.info/static/v1/data.json | \
        jq '[ .[] | select(.location.id==49 or .location.id==1033) ]' > upstream.json


**********
Downstream
**********
Running Luftdatenpumpe without reverse geocoding yields compact output,
while enabling geocoding will enrich the station information significantly.

Stations
========
::

    # No reverse geocoding.
    luftdatenpumpe stations --network=ldi --station=49,1033 > stations-compact.json

    # With reverse geocoding.
    luftdatenpumpe stations --network=ldi --station=49,1033 --reverse-geocode > stations-geocoded.json


Readings
========
::

    # No reverse geocoding.
    luftdatenpumpe readings --network=ldi --station=49,1033 > readings-compact.json

::

    # With reverse geocoding.
    luftdatenpumpe readings --network=ldi --station=49,1033 --reverse-geocode > readings-geocoded.json

