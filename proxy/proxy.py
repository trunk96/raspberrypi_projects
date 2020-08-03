from flask import Flask
from requests import get

app = Flask('__main__')
LOCAL_HOST = '127.0.0.1'

@app.route('/turn_off')
def proxy_turn_off():
    return get("http://127.0.0.1:8080").content

@app.route("/test")
def proxy_test():
    return get("http://127.0.0.1:8081").content

@app.route("/device_id")
def proxy_device_id():
    return get("http://127.0.0.1:8082").content

@app.route("/start_charging")
def proxy_start_charging():
    return get("http://127.0.0.1:8082/start_charging").content

@app.route("/stop_charging")
def proxy_stop_charging():
    return get("http://127.0.0.1:8082/stop_charging").content


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=80)
