from flask import Flask, request, jsonify
import requests
import json
import logging


app = Flask('__main__')
LOCAL_HOST = '127.0.0.1'

app_dict = {}

@app.route("/register_app", methods=["POST"])
def register_app():
    data = json.loads(request.get_json())
    app_name = data.get("name", "noname")
    app_addr = request.remote_addr
    app_dict[app_name] = app_addr
    app.logger.info("Registered app %s at address %s", app_name, app_addr)
    return "ok"

@app.route("/<app_name>/<path:text>", methods=["POST"])
def proxy_post(app_name, text):
    if app_name in app_dict:
        return requests.post("http://"+ app_dict[app_name]+"/"+text, json = request.get_json()).content
    return 'bad request!', 400

@app.route("/<app_name>/<path:text>", methods=["GET"])
def proxy_get(app_name, text):
    app.logger.info("GET call on /%s/%s", app_name, text)
    if app_name in app_dict:
        return requests.get("http://"+ app_dict[app_name]+"/"+text).content
    return 'bad request!', 400

@app.route("/")
def proxy_test():
    return requests.get("http://test_page/").content

if __name__ == '__main__':
    app.run()
else:
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
