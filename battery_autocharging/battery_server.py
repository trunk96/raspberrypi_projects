from flask import Flask
import requests

key_file = "key.txt"
turn_on_service = "turn_on_3"
turn_off_service = "turn_off_3"


app = Flask(__name__)

@app.route("/start_charging")
def start_charging():
    f = open(key_file)
    key = f.read()
    key = key.strip()
    f.close()

    r = requests.post("https://maker.ifttt.com/trigger/"+turn_on_service+"/with/key/"+key)
    return "{\"status\": \"Start Charging request sent\"}"
    
    

@app.route("/stop_charging")
def stop_charging():
    f = open(key_file)
    key = f.read()
    key = key.strip()
    f.close()

    r = requests.post("https://maker.ifttt.com/trigger/"+turn_off_service+"/with/key/"+key)
    return "{\"status\": \"Stop Charging request sent\"}"

if __name__=="__main__":
    app.run(host="127.0.0.1", port=8082)


