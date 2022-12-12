MQTT forwarding
===============
::

    luftdatenpumpe readings --stations=49,1033 --target=mqtt://mqtt.example.org/luftdaten.info


Result (reformatted for better readability)::

    mosquitto_sub -h mqtt.example.org -t '#' -v

    luftdaten.info {"latitude": 48.53, "longitude": 9.2, "altitude": 373.1, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u0ws16e5xx9n", "location_id": 49, "time": "2022-07-10T14:35:46Z", "sensor_id": 107, "sensor_type": "PPD42NS", "durP1": 100367.0, "ratioP1": 0.33, "P1": 174.21, "durP2": 0.0, "ratioP2": 0.0, "P2": 0.62}
    luftdaten.info {"latitude": 48.53, "longitude": 9.2, "altitude": 373.1, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u0ws16e5xx9n", "location_id": 49, "time": "2022-07-10T14:35:47Z", "sensor_id": 108, "sensor_type": "DHT22", "temperature": 24.1, "humidity": 1.0}
    luftdaten.info {"latitude": 48.53, "longitude": 9.2, "altitude": 373.1, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u0ws16e5xx9n", "location_id": 49, "time": "2022-07-10T14:36:02Z", "sensor_id": 417, "sensor_type": "SDS011", "P1": 7.8, "P2": 2.53}
    luftdaten.info {"latitude": 48.53, "longitude": 9.2, "altitude": 373.1, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u0ws16e5xx9n", "location_id": 49, "time": "2022-07-10T14:36:03Z", "sensor_id": 418, "sensor_type": "DHT22", "temperature": 25.0, "humidity": 20.3}

    luftdaten.info {"latitude": 52.56, "longitude": 13.374, "altitude": 44.3, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u33e0268hy1h", "location_id": 1033, "time": "2022-07-10T14:36:04Z", "sensor_id": 2055, "sensor_type": "SDS011", "P1": 3.4, "P2": 1.4}
    luftdaten.info {"latitude": 52.56, "longitude": 13.374, "altitude": 44.3, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u33e0268hy1h", "location_id": 1033, "time": "2022-07-10T14:36:05Z", "sensor_id": 2056, "sensor_type": "DHT22", "temperature": 20.2, "humidity": 3.9}
    luftdaten.info {"latitude": 52.56, "longitude": 13.374, "altitude": 44.3, "country": "DE", "exact_location": 0, "indoor": 0, "geohash": "u33e0268hy1h", "location_id": 1033, "time": "2022-07-10T14:36:05Z", "sensor_id": 67015, "sensor_type": "BME280", "temperature": 20.39, "pressure": 101364.47, "humidity": 41.09, "pressure_at_sealevel": 101888.09}

