from zeroconf import ServiceBrowser, Zeroconf
from flask import Flask
import requests

app = Flask(__name__)


shelly_list={}

class shelly_listener:
    def remove_service(self, zeroconf, type, name):
        name = name.split('.')[0]
        if name in shelly_list:
            del(shelly_list[name])

    def add_service(self, zeroconf, type, name):
        if ("shelly" in name) and (name not in shelly_list):
            name = name.split('.')[0]
            shelly_list[name] = name+".local"

@app.route("/")
def turn_off_shelly():
    payload = {'turn': 'off'}
    for shelly in shelly_list:
        r = requests.post("http://"+shelly_list[shelly]+"/relay/0", data = payload)


if __name__ == "__main__":
    zeroconf = Zeroconf()
    listener = shelly_listener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    app.run(host = '127.0.0.1', port=8080)
