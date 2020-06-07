from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def test():
    html = "<html>\n<head>\n<link rel=\"icon\" href=\"https://www.raspberrypi.org/homepage-9df4b/favicon.png\" \\>\n</head>\n<body>\n<h1 style=\"text-align:center;\">RaspberryPi Home Automation Server</h1>\n<h2 style=\"text-align:center;\">Test Page</h2>\n<ul>"
    response = requests.get("http://127.0.0.1:8080/get_shellies")
    shelly_list = response.json()
    for shelly in shelly_list:
        html += "<li>"+shelly+"</li>"
    html += "</ul>\n</body>\n</html>"
    return html

if __name__ == "__main__":
    app.run(host = "127.0.0.1", port = 8081)

