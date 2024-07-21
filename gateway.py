from common.base_app import BaseApp
from common.frequency import Frequency
from common.timing import get_datetime, get_days_since
from common.topics import *
from tinydb import TinyDB, Query
from Adafruit_IO import Client, Feed
import json
import os
import time


class Gateway(BaseApp):
    def __init__(self):
        self._db = None
        self._bus_table = None
        self._station_table = None
        self.aio = None
        self._frequency = None

        # Init app
        BaseApp.__init__(self)

    def on_connected(self):
        #  Open database tables
        self._db = TinyDB('data/db.json')
        self._bus_table = self._db.table('bus')
        self._station_table = self._db.table('station')

        # Connect to adafruit io
        self.aio = Client(os.getenv("ADAFRUIT_IO_USERNAME"), os.getenv("ADAFRUIT_IO_KEY"))

        # Setup frequency model
        self._frequency = Frequency(self)

        # Subscribe to registration topics
        self.mqtt_client.subscribe(TOPIC_STATION_REG)
        self.mqtt_client.subscribe(TOPIC_STATION_DEREG)
        self.mqtt_client.subscribe(TOPIC_BUS_REG)
        self.mqtt_client.subscribe(TOPIC_BUS_DEREG)

        # Request nodes to register themselves.
        print('Asking nodes to reveal themselves')
        self.mqtt_client.publish(TOPIC_REQUEST_REG)
    
    def on_message(self, topic, payload):
        BaseApp.on_message(self, topic, payload)
        
        if topic == TOPIC_BUS_REG:
            # Subscribe to bus' counter topic
            self.mqtt_client.subscribe(TOPIC_BUS_COUNTER % payload)

            # Try create an adafruit IO feed
            feed = Feed(name='cm2110-bus-%s' % payload)
            try:
                self.aio.create_feed(feed)
                print('Adafruit IO feed created for new bus!')
            except:
                pass

            print('Registered bus %s' % payload)
        elif topic == TOPIC_BUS_DEREG:
            self.mqtt_client.unsubscribe(TOPIC_BUS_COUNTER % payload)
            print('De-registered bus %s' % payload)
        elif topic == TOPIC_STATION_REG:
            self.mqtt_client.subscribe(TOPIC_STATION_COUNTER % payload)
            print('Registered station %s' % payload)

            # Try create an adafruit IO feed
            feed = Feed(name='cm2110-station-%s' % payload)
            try:
                self.aio.create_feed(feed)
                print('Adafruit IO feed created for new station!')
            except:
                pass

        elif topic == TOPIC_STATION_DEREG:
            self.mqtt_client.unsubscribe(TOPIC_STATION_COUNTER % payload)
            print('De-registered station %s' % payload)
        elif TOPIC_BUS_COUNTER_CHK in topic:
            # Save to tinydb for modelling
            busid = topic.replace(TOPIC_BUS_COUNTER_CHK, '')
            data = json.loads(payload)
            data['id'] = busid
            self._bus_table.insert(data)

            # Send to adafruit io
            self.aio.send('cm2110-bus-%s' % busid, data['percentage'] * 100) # *100 so it displays nicely on the panel

            # Forward the data to the web topic
            self.mqtt_client.publish(TOPIC_WEB_BUS_COUNTER % busid, payload, retain=True)
        elif TOPIC_STATION_COUNTER_CHK in topic:
            # Save to tinydb for modelling
            stationid = topic.replace(TOPIC_STATION_COUNTER_CHK, '')
            data = json.loads(payload)
            data['id'] = stationid
            self._station_table.insert(data)

            # Send to adafruit io
            self.aio.send('cm2110-station-%s' % stationid, data['count'])

    def run(self):
        while self.mqtt_client.connected_flag:
            # Get the recommendation trigger data
            data = self.aio.receive('cm2110-recommend-trigger')

            if int(data.value) == 1:
                print('Recommendations were requested!')
                self._frequency.get_prediction()

            time.sleep(0.5)

    def get_route_data(self, route):
        query = Query()
        # Get data for route from the last 24 hours.
        return self._bus_table.search((query.route == route) & (query.timestamp.map(lambda d: get_days_since(get_datetime(d))) < 1))


# Create and run the gateway
app = Gateway()
app.run()
