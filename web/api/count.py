from http.server import BaseHTTPRequestHandler
import paho.mqtt.client as mqtt
import os
import time
import ssl
from urllib.parse import urlparse, parse_qs
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Get the bus we want info for from the query string.
        bus = parse_qs(urlparse(self.path).query).get('bus', None)

        # If the bus was not specified, 404 error.
        if (bus == None):
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Must specify bus'.encode())
            return

        # Create mqtt client and setup credentials
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(os.getenv("MQTT_USER_NAME"), os.getenv("MQTT_PASSWORD"))
        
        # Enable tls if the server supports it.
        if os.getenv("MQTT_TLS") == "True":
            self.mqtt_client.tls_set(cert_reqs = ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
            self.mqtt_client.tls_insecure_set(False)
        
        # Register event hooks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message

        # Connect to the broker.
        try:
            self.mqtt_client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT")), keepalive = 60)
        except:
            self.write_json(500, {'error': 'Broker connection failed!'})
            return

        # Prepare MQTT loop.
        self.mqtt_client.connected_flag = False
        self.mqtt_client.failed_flag = False
        self.mqtt_client.loop_start()

        # Wait for the connection to open.
        timeout = time.time() + 5
        while not self.mqtt_client.connected_flag:
            # If connection has failed, kill the handler
            if self.mqtt_client.failed_flag:
                return

            if time.time() > timeout:
                self.write_json(500, {'error': 'Broker connection timed out!'})
                return
            
            # Wait for 0.25s. So small as every second counts in our serverless function
            time.sleep(0.25)

        topic = 'web/bus/counter/%s' % (bus[0])

        # Set found flag to false
        self._found_data = False

        # Subscribe to the bus' topic. The last retained message will be sent to our client.
        print('Subscribing to %s' % topic)
        self.mqtt_client.subscribe(topic)

        # Wait for the response for 5 seconds.
        timeout = time.time() + 5
        while not self._found_data and time.time() < timeout:
            time.sleep(0.5)

        # If the data was not found, write 404 error.
        if not self._found_data:
            print('Timed out!')
            self.write_json(404, {'error': 'No data.'})
        
        # Close the MQTT client down.
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        # Check connection result        
        if rc == 0:
            self.mqtt_client.connected_flag = True
            print("Connected successfully")            
            return
        
        print("Failed to connect, rc=%s" % (rc))

        # Write error response.
        self.write_json(500, {'error': 'Broker connection failed!'})

        # Stop the connection wait.
        self.mqtt_client.failed_flag = True

    def write_json(self, code, message):
        # Write error response.
        self.send_response(code)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write(json.dumps(message).encode())

    def _on_message(self, client, userdata, msg):
        if (self._found_data):
            return
        print('Message received!')

        data = json.loads(msg.payload.decode("utf-8"))

        # Construct JSON response. We skip count for the web side
        self.write_json(200, {'timestamp': data['timestamp'], 'percentage': data['percentage']})

        # We found data!
        self._found_data = True
