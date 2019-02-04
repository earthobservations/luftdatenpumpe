# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import os
import json
import logging
from munch import Munch
from pprint import pformat
import paho.mqtt.client as mqtt

try:
    from urlparse import urlsplit
except ImportError:
    from urllib.parse import urlsplit

log = logging.getLogger(__name__)


class MQTTAdapter(object):

    capabilities = ['readings']

    def __init__(self, uri, keepalive=60, client_id_prefix=None, dry_run=False):

        address = urlsplit(uri)
        self.host       = address.hostname
        self.port       = address.port or 1883
        self.username   = address.username
        self.password   = address.password
        self.topic      = address.path

        self.keepalive  = keepalive

        self.client_id_prefix = client_id_prefix or 'luftdatenpumpe'

        self.dry_run = dry_run

        self.connect()

    def emit(self, reading):
        """
        Will publish these kind of messages to the MQTT bus:
        {
            "time": "2018-12-03T01:49:00Z",
            "location_id": 9564,
            "sensor_id": 18870,
            "sensor_type": "DHT22",
            "geohash": "u3qcs53rp",
            "altitude": 85.0,
            "temperature": 2.8,
            "humidity": 90.5
        }
        """

        # Build MQTT message.
        message = Munch()

        # Station info
        for key, value in reading.station.items():
            if isinstance(value, dict):
                message.update(value)
            else:
                message[key] = value

        message['location_id'] = message['station_id']
        del message['station_id']

        # Measurement fields
        message.update(reading.data)

        # Publish to MQTT bus.
        if self.dry_run:
            log.info('Dry-run. Would publish record:\n{}'.format(pformat(message)))
        else:
            # FIXME: Don't only use ``sort_keys``. Also honor the field names of the actual readings by
            # putting them first. This is:
            # - "P1" and "P2" for "sensor_type": "SDS011"
            # - "temperature" and "humidity" for "sensor_type": "DHT22"
            # - "temperature", "humidity", "pressure" and "pressure_at_sealevel" for "sensor_type": "BME280"
            mqtt_message = json.dumps(message)
            self.publish(mqtt_message)

    def flush(self, final=False):
        pass

    def connect(self):

        if self.dry_run:
            return

        # Create a mqtt client object
        pid = os.getpid()
        client_id = '{}:{}'.format(self.client_id_prefix, str(pid))
        self.mqttc = mqtt.Client(client_id=client_id, clean_session=True)

        # Handle authentication
        if self.username:
            self.mqttc.username_pw_set(self.username, self.password)

        # Connect to broker
        self.mqttc.connect(self.host, self.port, self.keepalive)

        self.mqttc.loop_start()

    def close(self):
        self.mqttc.disconnect()

    def effective_topic(self, topic=None):
        parts = []
        base_topic = self.topic.strip(u'/')
        if base_topic:
            parts.append(base_topic)
        if topic:
            parts.append(topic)
        return u'/'.join(parts)

    def publish(self, message, topic=None):
        topic = self.effective_topic(topic)
        log.debug('Publishing to topic "{}": {}'.format(topic, message))
        return self.mqttc.publish(topic, message)

    def subscribe(self, topic=None):
        topic = self.effective_topic(topic)
        log.info('Subscribing to topic "{}"'.format(topic))
        return self.mqttc.subscribe(topic)
