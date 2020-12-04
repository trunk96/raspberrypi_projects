from zeroconf import ServiceBrowser, Zeroconf
from flask import Flask
import requests
import json
import logging

app = Flask(__name__)
RPI_PROXY = "rpi_proxy"

shelly_list={}

class shelly_listener:
    def remove_service(self, zeroconf, type, name):
        name = name.split('.')[0]
        if name in shelly_list:
            del(shelly_list[name])

    def add_service(self, zeroconf, type, name):
        if ("shelly" in name) and (name not in shelly_list):
            app.logger.info("Added a Shelly")
            name = name.split('.')[0]
            shelly_list[name] = name#+".local"

@app.route("/turn_off")
def turn_off_shelly():
    payload = {'turn': 'off'}
    for shelly in shelly_list:
        r = requests.post("http://"+shelly_list[shelly]+"/relay/0", data = payload)
    return app.send_static_file("index.html")

@app.route("/favicon.ico")
def route_favicon():
    return app.send_static_file("favicon.ico")

@app.route("/get_shellies")
def get_shellies():
    shellies = json.dumps(shelly_list)
    return shellies

def worker():
    global zeroconf
    global listener
    global browser
    zeroconf = Zeroconf()
    listener = shelly_listener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    data = {"name": "lights_control", "route": "turn_off"}
    requests.post("http://"+RPI_PROXY+"/register_app", json = json.dumps(data))

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=80)
else:
    guicorn_logger = logging.getLogger('guicorn.error')
    app.logger.handlers = guicorn_logger.handlers
    app.logger.setLevel(guicorn_logger.level)
    worker()
    
    
