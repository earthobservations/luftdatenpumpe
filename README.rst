==============
Luftdatenpumpe
==============


About
=====
Request data from live API of luftdaten.info, enrich with geospatial information and publish to MQTT bus.


References
==========
- http://luftdaten.info/
- http://archive.luftdaten.info/
- http://deutschland.maps.luftdaten.info/
- https://getkotori.org/docs/applications/luftdaten.info/
- https://luftdaten.hiveeyes.org/grafana/d/bEe6HJamk/feinstaub-verlauf-berlin
- https://luftdaten.hiveeyes.org/grafana/d/000000004/feinstaub-karte-deutschland

.. seealso::

    `Support for InfluxDB and MQTT as backend <https://github.com/opendata-stuttgart/sensors-software/issues/33#issuecomment-272711445>`_.


Setup
=====
Install Python modules::

    pip install docopt==0.6.2 requests==2.13.0 paho-mqtt==1.2 Geohash==1.0 geopy==1.11.0 Beaker==1.8.1 tqdm==4.11.2


Synopsis
========
::

    luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten.info --progress

    2017-04-22 03:53:47,947 [kotori.vendor.luftdaten.luftdatenpumpe] INFO   : Publishing data to MQTT URI mqtt://mqtt.example.org/luftdaten.info
    2017-04-22 03:53:49,012 [kotori.vendor.luftdaten.luftdatenpumpe] INFO   : Timestamp of first record: 2017-04-22T01:48:02Z
    100%|..........................................................................| 6617/6617 [00:01<00:00, 4184.30it/s]

Result (reformatted for better readability)::

    mosquitto_sub -h mqtt.example.org -t 'luftdaten.info/#' -v

    /luftdaten.info {"humidity": 42.2, "temperature": 12.0,     "location_id":  49, "sensor_id":  418, "sensor_type": "DHT22",  "time": "2017-04-21 23:49:01"}
    /luftdaten.info {"P1": 7.5, "P2": 6.42,                     "location_id": 919, "sensor_id": 1799, "sensor_type": "SDS011", "time": "2017-04-21 23:49:01"}
    # [...]


Advanced usage
==============


With authentication
-------------------
::

    luftdatenpumpe forward --mqtt-uri mqtt://username:password@mqtt.example.org/luftdaten.info


WAN topology
------------
WAN addressing with geospatial data enrichment::

    --geohash                 Compute Geohash from latitude/longitude and add to MQTT message
    --reverse-geocode         Compute geographical address using the Nominatim reverse geocoder and add to MQTT message

Suitable for data acquisition with Kotori and InfluxDB. Display with Grafana Worldmap Panel.

.. seealso::

    - https://github.com/vinsci/geohash/
    - https://github.com/openstreetmap/Nominatim
    - https://github.com/daq-tools/kotori
    - https://github.com/influxdata/influxdb
    - https://github.com/grafana/grafana
    - https://grafana.com/plugins/grafana-worldmap-panel

Publisher::

    luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten/testdrive/earth/42/data.json --geohash --reverse-geocode --progress

    2017-04-22 03:55:50,426 [kotori.vendor.luftdaten.luftdatenpumpe] INFO   : Publishing data to MQTT URI mqtt://mqtt.example.org/luftdaten/testdrive/earth/42/data.json
    2017-04-22 03:55:51,396 [kotori.vendor.luftdaten.luftdatenpumpe] INFO   : Timestamp of first record: 2017-04-22T01:50:02Z
    100%|..........................................................................| 6782/6782 [01:01<00:00, 109.77it/s]

Subscriber::

    mosquitto_sub -h mqtt.example.org -t 'luftdaten/testdrive/#' -v

    luftdaten/testdrive/earth/42/data.json {"sensor_id": 778,  "location_name": "Alte Landstra\u00dfe, Bludesch, Vorarlberg, AT",          "temperature": 18.9, "time": "2017-03-29T15:29:02", "geohash": "u0qutbdmbb5s", "location_id": 372, "humidity": 43.2}
    luftdaten/testdrive/earth/42/data.json {"sensor_id": 1309, "location_name": "Unterer Rosberg, Waiblingen, Baden-W\u00fcrttemberg, DE", "temperature": 27.7, "time": "2017-03-29T15:29:02", "geohash": "u0wtgfygz1rr", "location_id": 647, "humidity": 1.0}
    # [...]

Now::

    luftdaten.info {"time": "2018-12-03T01:50:31Z", "location_id": 28,   "sensor_id": 658,  "sensor_type": "SDS011", "geohash": "u0wt6pv2qqhz", "altitude": 223.7, "P1": 0.8, "P2": 0.6}
    luftdaten.info {"time": "2018-12-03T01:50:32Z", "location_id": 28,   "sensor_id": 657,  "sensor_type": "DHT22",  "geohash": "u0wt6pv2qqhz", "altitude": 223.7, "humidity": 99.9, "temperature": 12.4}
    luftdaten.info {"time": "2018-12-03T01:52:17Z", "location_id": 1071, "sensor_id": 2129, "sensor_type": "SDS011", "geohash": "u33dbm6duz90", "altitude": 38.7,  "P1": 5.62, "P2": 5.05}
    luftdaten.info {"time": "2018-12-03T01:52:17Z", "location_id": 1071, "sensor_id": 2130, "sensor_type": "DHT22",  "geohash": "u33dbm6duz90", "altitude": 38.7,  "humidity": 97.6, "temperature": 12.4}



License
=======

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU Affero General Public License
   along with this program; if not, see:
   <http://www.gnu.org/licenses/agpl-3.0.txt>,
   or write to the Free Software Foundation,
   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA


Data schema
===========
The data schema offered by `https://api.luftdaten.info/static/v1/data.json` is like this.

Example for DHT22 sensor::

    {
        "id": 59625316,
        "location": {
            "id": 312,
            "latitude": "48.647",
            "longitude": "9.445"
        },
        "sampling_rate": null,
        "sensor": {
            "id": 660,
            "pin": "7",
            "sensor_type": {
                "id": 9,
                "manufacturer": "various",
                "name": "DHT22"
            }
        },
        "sensordatavalues": [
            {
                "id": 169745466,
                "value": "44.30",
                "value_type": "humidity"
            },
            {
                "id": 169745465,
                "value": "15.80",
                "value_type": "temperature"
            }
        ],
        "timestamp": "2017-03-30T19:24:02"
    }

Example for SDS011 sensor::

    {
        "id": 59625314,
        "location": {
            "id": 220,
            "latitude": "48.741",
            "longitude": "9.317"
        },
        "sampling_rate": null,
        "sensor": {
            "id": 467,
            "pin": "1",
            "sensor_type": {
                "id": 14,
                "manufacturer": "Nova Fitness",
                "name": "SDS011"
            }
        },
        "sensordatavalues": [
            {
                "id": 169745461,
                "value": "6.73",
                "value_type": "P1"
            },
            {
                "id": 169745462,
                "value": "4.48",
                "value_type": "P2"
            }
        ],
        "timestamp": "2017-03-30T19:24:02"
    },
