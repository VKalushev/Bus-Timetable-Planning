# Bus Timetable Planning
## Definitely Not Internet Pi-rates
Our members are Connor Mackay, Connor McHattie, Vasil Kalushev and Reece Mackie.

## Our Project
We have created a system that will detect people as they wait at a bus stop and track people getting on/off buses to deterimine how many people are on those buses. This would then collect the data and pass it to Adafruit and our website. Our prediction model can then be used on the collected data to figure out how often buses should be running on a given route.

## Why it's Useful
Our project would be useful for prospective passengers to see whether the bus they're waiting to catch is already full, or if there will be space for them. For the bus company, they will be able to have the optimimum number of buses running on each route.

## Advanced Features
For our advanced features we opted to:
- Use OpenCV Object Detection and Tracking to count people in our 3 edge nodes.
- Use Vercel to host a publicly viewable webpage showing the number of people on a bus utilising MQTT on the backend.

## Hardware Required
For the minimum of 1 Bus Node, 2 Station Nodes and 1 Gateway, the following hardware is required:
- 4x Raspbery Pi
- 3x Pi Camera
- 1x Sense Hat

## Setup
To begin, run `pip3 install -r requirements.txt` to install the required packages. This enables a Pi to run any of the programs in the repo.

You must also install these packages on the Pi:
```sh
sudo apt-get update
sudo apt-get install sense-hat python3-h5py libatlas-base-dev
sudo reboot
```

To setup your PiCamera, you may have to enable legacy camera. You can run this:
```sh
sudo raspi-config
```
You want to navigate to Interfaces and then enable the legacy camera option. You should then reboot your Pi.

Finally you must configure the `.env` file to use the correct broker.

## Running the project
### Gateway
The gateway recieves messages from all the edge nodes and passes the data to the website, TinyDB and Adafruit. To run the gateway, run `python3 gateway.py`.

### Bus Node
The Bus Node counts the number of people currently on the bus by tracking people who get on and off the bus with a camera. The tracking system needs to be turned on by pressing the joystick in the middle position, and the tracking can be switched between tracking people getting on / off by clicking right or left on the joystick. The sense hat lights up blue for people getting on and red for people getting off.

You'll need to have a config file, an example of this is provided in the config folder. To run a bus node, run `python3 bus_node.py configs/<config file>.yaml`. 

### Station Node
The station node counts the number of people detected using a camera.

You'll need to have a config file, an example of this is provided in the config folder. To run a station node, run `python3 station_node.py configs/<config file>.yaml`.

## The web interface
This is hosted at https://cm2110-dnip.vercel.app/?bus=1

The web API and interface (code stored in the `web` directory) is deployed to vercel using their CLI.

How to work with vercel CLI:
```sh
# Installing
npm i -g vercel

# Publish to develop
vercel

# Publish to production
vercel --prod

# Local development
vercel dev
```

In order to run this, you must set the following environment variables on vercel:
```sh
MQTT_HOST # The hostname/IP of the MQTT broker.
MQTT_USER_NAME # The username to authenticate with.
MQTT_PASSWORD # The password to authenticate with.
MQTT_PORT # The port to connect on.
MQTT_TLS # Whether to use TLS.
```

The api directory has a python script that can interact with the MQTT broker and is exposed as a serverless function. The `requirements.txt` tells vercel to make the mqtt library available to our serverless function.
MQTT credentials are stored securely as environment variables.

Vercel operates a passwordless login process, so it is not possible for me to provide access to the panel.

## Adafruit
Adafruit is used to store our data and also its dashboard feature is used to evaluate the systems data.

Login details for the dashboard:
- Username: `Gninjar`
- Password: `IoT2022`

Relevant feeds are prefixed with `cm2110` and the relevant dashboard is called `IoT Dashboard`.

**We as a group have decided we have no interest in sharing this project with CENSIS.**
