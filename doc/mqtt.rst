MQTT forwarding
===============
::

    luftdatenpumpe forward --stations=28,1071 --target=mqtt://mqtt.example.org/luftdaten.info


Result (reformatted for better readability)::

    mosquitto_sub -h mqtt.example.org -t '#' -v

    luftdaten.info {"station_id": 28,   "sensor_id": 658,  "sensor_type": "SDS011", "latitude": 48.778, "longitude": 9.236,  "altitude": 223.7, "country": "DE", "geohash": "u0wt6pv2qqhz", "time": "2018-12-06T23:49:05Z", "P1": 1.67, "P2": 1.5}
    luftdaten.info {"station_id": 28,   "sensor_id": 657,  "sensor_type": "DHT22",  "latitude": 48.778, "longitude": 9.236,  "altitude": 223.7, "country": "DE", "geohash": "u0wt6pv2qqhz", "time": "2018-12-06T23:49:05Z", "humidity": 99.9, "temperature": 12.3}
    luftdaten.info {"station_id": 1071, "sensor_id": 2129, "sensor_type": "SDS011", "latitude": 52.544, "longitude": 13.374, "altitude": 38.7,  "country": "DE", "geohash": "u33dbm6duz90", "time": "2018-12-06T23:48:33Z", "P1": 16.7, "P2": 14.97}
    luftdaten.info {"station_id": 1071, "sensor_id": 2130, "sensor_type": "DHT22",  "latitude": 52.544, "longitude": 13.374, "altitude": 38.7,  "country": "DE", "geohash": "u33dbm6duz90", "time": "2018-12-06T23:48:33Z", "humidity": 93.1, "temperature": 11.5}

::

    mqtt://mqtt.example.org/luftdaten/testdrive/earth/42/data.json
