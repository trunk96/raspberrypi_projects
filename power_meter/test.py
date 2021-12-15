import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected to the broker!")
    client.subscribe("home/prism/energy_data/power_grid")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode()))
    

print("Starting...")
client = mqtt.Client()
client.connect("127.0.0.1", 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
