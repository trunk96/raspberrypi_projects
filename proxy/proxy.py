from flask import Flask
from requests import get

app = Flask('__main__')
LOCAL_HOST = '127.0.0.1'

@app.route('/turn_off')
def proxy_turn_off():
    return get("http://127.0.0.1:8080").content


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=80)
