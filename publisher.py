import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

TEMPERATURE_TOPIC = "sensors/temperature"
HUMIDITY_TOPIC = "sensors/humidity"

client = mqtt.Client()

client.connect(BROKER, PORT, 60)

print("Connected to EMQX")
print("Publishing sensor data...")

while True:
    temperature = round(random.uniform(25, 35), 2)
    humidity = round(random.uniform(40, 70), 2)

    client.publish(TEMPERATURE_TOPIC, str(temperature))
    client.publish(HUMIDITY_TOPIC, str(humidity))

    print(f"Temperature: {temperature} °C | Humidity: {humidity} %")

    time.sleep(2)
