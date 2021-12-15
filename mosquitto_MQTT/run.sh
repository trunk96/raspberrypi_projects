#!/bin/bash
docker run -d -it -p 1883:1883 -p 9001:9001 -v /home/emanuele/projects/mosquitto_MQTT/:/mosquitto --restart unless-stopped --name mosquitto_MQTT eclipse-mosquitto 
