from common.base_app import BaseApp
from common.timing import get_timestamp;
from common.topics import *
from common.ignore_region import IgnoreRegion
from common.capture import Capture
from common.tracker import Tracker
import cv2 as cv
import sys
import yaml
from sense_hat import SenseHat
import datetime
import time

NUM_TRACKED_FRAMES = 31 # The number of frames to run the track for before running detect again


class Bus(BaseApp):
    def __init__(self, config):
        # Store config and initialise counter
        self._config = config

        # Init.
        self._passenger_count = 0

        # Wait until init
        self._initialized = False

        # Setup
        BaseApp.__init__(self)

    def on_connected(self):        
        # Register to the registration request topic.
        self.mqtt_client.subscribe(TOPIC_REQUEST_REG)

        # Send registration in case the gateway is running
        self.send_registration()

        # Set will message
        self.mqtt_client.will_set(TOPIC_BUS_DEREG, self._config['id'])

        # Init camera capture
        self._capture = Capture()
        image = self._capture.read()
        
        # Setup Ignore Regions, use config data (if any)
        self._entering_ir_pos = self._config["ir_entering_position"]
        self._leaving_ir_pos = self._config["ir_leaving_position"]
        self._ir_ratio = self._config["ir_ratio"]
        
        self._entering_ignore_region = None
        self._leaving_ignore_region = None
        
        if self._entering_ir_pos is not None:
            self._entering_ignore_region = IgnoreRegion(image=image, position=self._entering_ir_pos, ratio=self._ir_ratio)
        else:
            self._entering_ignore_region = IgnoreRegion(image=image)
        
        if self._leaving_ir_pos is not None:
            self._leaving_ignore_region = IgnoreRegion(image=image, position=self._leaving_ir_pos, ratio=self._ir_ratio)
        else:
            self._leaving_ignore_region = IgnoreRegion(image=image)
        
        self._tracker = Tracker(capture=self._capture, ignore_region=self._entering_ignore_region)

        self._is_entering = True # Is the tracker tracking people who are entering the bus?
        self.is_tracking_enabled = False
        
        self._sense_hat = SenseHat()
        self._sense_hat.clear()

        self._initialized = True
        print('Node initialized')

    def send_registration(self):
        print('Sending registration..')
        self.publish_json(TOPIC_BUS_REG, self._config['id'])
    
    def on_message(self, topic, payload):
        BaseApp.on_message(self, topic, payload)

        if topic == TOPIC_REQUEST_REG:
            print('Gateway requested registration. Sending...')
            self.send_registration()

    def send_count(self):
        self.publish_json(TOPIC_BUS_COUNTER % self._config['id'], {
            'timestamp': get_timestamp(),
            'route': self._config['route'],
            'percentage': self._passenger_count / self._config['capacity']
        }, retain=True)
        print('Occupancy pushed to gateway.')
    
    def check_sense_hat(self):
        for event in self._sense_hat.stick.get_events():
            if event.action == 'pressed':
                if event.direction == "right": # Toogle Passengers Entering
                    self._sense_hat.clear((0, 0, 255))
                    self._is_entering = True
                    self._tracker.reset(capture=self._capture, ignore_region=self._entering_ignore_region)
                elif event.direction == "left": # Toggle Passengers Leaving
                    self._sense_hat.clear((255, 0, 0))
                    self._is_entering = False
                    self._tracker.reset(capture=self._capture, ignore_region=self._leaving_ignore_region)
                elif event.direction == "middle": # Toggle Tracking On/Off
                    if self.is_tracking_enabled:
                        self.is_tracking_enabled = False
                        self._sense_hat.clear()
                    else:
                        self.is_tracking_enabled = True
                        self._sense_hat.clear((0, 0, 255))
    
    def run(self):
        last_time = datetime.datetime.now()
        
        while self.mqtt_client.connected_flag:
            # Wait 
            if not self._initialized:
                time.sleep(1)
            if self.is_tracking_enabled:
                # Detect any people
                self._tracker.detect()
                self.check_sense_hat()
                
                for _ in range(NUM_TRACKED_FRAMES):
                    # Track the detected people for a frame
                    track_result = self._tracker.track()

                    # Demo draw.
                    if self._config['debug']:
                        self._tracker.draw_and_show()

                    num_who_just_left = track_result["num_who_just_left_feed"]

                    # Increment passenger count
                    if self._is_entering:
                        self._passenger_count += num_who_just_left
                        if num_who_just_left > 0:
                            print('Person entered')
                    else:
                        self._passenger_count -= num_who_just_left

                        if num_who_just_left > 0:
                            print('Person left')
                        
                        if self._passenger_count < 0:
                            self._passenger_count = 0
                    
                    self.check_sense_hat()
                    
            self.check_sense_hat()

            # Wait for opencv to catch up        
            cv.waitKey(1)
            
            time_difference = datetime.datetime.now() - last_time
            
            if time_difference.total_seconds() > 5:
                last_time = datetime.datetime.now() # Reset the timer
                if self.is_tracking_enabled:
                    self.send_count()
        
# Get config file from command line args
if (len(sys.argv) < 2):
    print('Error: Must provide config file path in CLI arguments.')
    sys.exit(-1)

# Load yaml config
with open(sys.argv[1], 'r') as file:
    config = yaml.safe_load(file)

# Start bus node
app = Bus(config)
app.run() 
cv.destroyAllWindows()
