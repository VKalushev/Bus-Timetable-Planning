import time
import ssl
import sys
import os
import json

import paho.mqtt.client as mqtt
from dotenv import load_dotenv


# The base application for all the other applications to base off of
# Exposes an MQTT connection.
class BaseApp:
    def __init__(self):
        # Load .env file for mqtt and adafruit credentials
        load_dotenv()

        # Init MQTT client
        self._setup_mqtt(os.getenv("MQTT_USER_NAME"), os.getenv("MQTT_PASSWORD"), os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")), os.getenv("MQTT_SSL"))

    def _setup_mqtt(self, user_name, password, host, port, tls_enabled):
        print("Connecting to %s:%s as %s"%(host, port, user_name))

        # Create client and set credentials
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(user_name, password)
        
        # Enable tls if the server supports it.
        if tls_enabled == "True":
            self.mqtt_client.tls_set(cert_reqs = ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
            self.mqtt_client.tls_insecure_set(False)
        
        # Register event hooks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message

        # Attempt connect and start worker thread
        self.mqtt_client.connect(host, port, keepalive = 60)
        self.mqtt_client.connected_flag = False
        self.mqtt_client.loop_start()

        # Wait for the connection to open.
        while not self.mqtt_client.connected_flag:
            time.sleep(1)
        
    def _on_connect(self, client, userdata, flags, rc):
        # Check for success        
        if rc == 0:
            self.mqtt_client.connected_flag = True
            print("Connected successfully")          
            self.on_connected()  
            return
        print("Failed to connect, rc=%s" % (rc))
        sys.exit(-1)

    def _on_message(self, client, userdata, msg):
        # Decode the payload into a string and offload to the handler
        payload = str(msg.payload.decode("utf-8"))
        self.on_message(msg.topic, payload)
        
    def on_message(self, topic, payload):
        print("Received \"%s\" from topic %s"%(payload, topic))

    # Override if you want the app to do something.
    def run(self):
        while self.mqtt_client.connected_flag:
            time.sleep(1)

    # Publish an object as a json string over the MQTT client.
    def publish_json(self, topic, object, retain = False):
        self.mqtt_client.publish(topic, json.dumps(object), retain=retain)
