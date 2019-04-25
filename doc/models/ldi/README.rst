######################################
Data models for luftdaten.info network
######################################


********
Upstream
********
::

    http https://api.luftdaten.info/static/v1/data.json | jq '.[] | select(.location.id==28 or .location.id==1071)'


**********
Downstream
**********

Stations
========
::

    # No reverse geocoding. Compact output.
    luftdatenpumpe stations --network=ldi --station=28,1071 > stations-egress-compact.json

    # With reverse geocoding. Extended output.
    luftdatenpumpe stations --network=ldi --station=28,1071 --reverse-geocode > stations-egress-geocoded.json


Readings
========
::

    # No reverse geocoding. Compact output.
    luftdatenpumpe readings --network=ldi --station=28,1071 > readings-egress-compact.json

::

    # With reverse geocoding. Extended output.
    luftdatenpumpe readings --network=ldi --station=28,1071 --reverse-geocode > readings-egress-geocoded.json
