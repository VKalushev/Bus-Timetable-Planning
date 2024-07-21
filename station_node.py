import datetime
from common.base_app import BaseApp
from common.topics import *
from common.timing import get_timestamp
from common.capture import Capture
from common.tracker import Tracker
import cv2 as cv
import sys
import yaml
import time


class Station(BaseApp):
    def __init__(self, config):
        # Save config
        self._config = config

        # Setup
        BaseApp.__init__(self)

        # Initialise the capture of the camera feed
        self._capture = Capture()
        
        # Initialise the tracker that detects / tracks people
        self._tracker = Tracker(capture=self._capture)
    
    def on_connected(self):
        # Register to the registration request topic.
        self.mqtt_client.subscribe(TOPIC_REQUEST_REG)

        # Send registration in case the gateway is running
        self.send_registration()
        
        # Set will message
        self.mqtt_client.will_set(TOPIC_STATION_DEREG, self._config['id'])

    def on_message(self, topic, payload):
        BaseApp.on_message(self, topic, payload)

        if topic == TOPIC_REQUEST_REG:
            print('Gateway requested registration. Sending...')
            self.send_registration()

    def send_registration(self):
        self.mqtt_client.publish(TOPIC_STATION_REG, self._config['id'])

    def send_count(self, count):
        self.publish_json(TOPIC_STATION_COUNTER % self._config['id'], {
            'timestamp': get_timestamp(),
            'count': count
        })

    def run(self):
        # Initialize last_time. Used to limit data send rate
        last_time = datetime.datetime.now()
    
        while self.mqtt_client.connected_flag:
            # Get a dictionary of the results of tracking people in the current frame
            detect_results = self._tracker.detect_once()

            # Debug draw
            if self._config['debug']:
                self._tracker.draw_and_show()
            
            # OpenCV wait
            cv.waitKey(1)
            
            # Get the number of people at the station
            count = detect_results["num_detected"]
            print('People detected: %d' % count)

            # Get time difference
            time_difference = datetime.datetime.now() - last_time
            
            # Send data every 10 seconds
            if time_difference.total_seconds() > 10:
                last_time = datetime.datetime.now() # Reset the timer
                self.send_count(count)


# Get config file from command line args
if len(sys.argv) < 2:
    print('Error: Must provide config file path in CLI arguments.')
    sys.exit(-1)

# Load yaml config
with open(sys.argv[1], 'r') as file:
    config = yaml.safe_load(file)

# Start the station node
app = Station(config)
app.run()
cv.destroyAllWindows()
