#!/usr/bin/env python3
import random
import socket
import time
import paho.mqtt.client as mqtt

class MyMQTTPublisher:

    def __init__(self,  topic, sleep_time, sleep_time_sd):
        self.client = mqtt.Client()
        self.topic = topic
        self.sleep_time = sleep_time
        self.sleep_time_sd = sleep_time_sd
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        print(mqtt.connack_string(rc))

    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected with result code {rc}")
        if rc != 0:
            print("Unexpected disconnection.")

    def connect(self):
        self.client.connect(host='127.0.0.1', port=5020, keepalive=100)

    def start_publishing(self):
        self.client.loop_start()

        while True:
            message = f"{random.gauss(10, 1):.2f}"
            sleep_time = random.gauss(self.sleep_time, self.sleep_time_sd)
            sleep_time = self.sleep_time if sleep_time < 0 else sleep_time
            time.sleep(sleep_time)

            self.client.publish(topic=self.topic, payload=message)

    def stop_publishing(self):
        self.client.loop_stop()

if __name__ == "__main__":
    config = {"MQTT_BROKER_ADDR": "127.0.0.1:5020", "MQTT_TOPIC_PUB": "test/topic", "SLEEP_TIME": 1,
              "SLEEP_TIME_SD": 0.1, "HOSTNAME": socket.gethostname()}

    for c in ("SLEEP_TIME", "SLEEP_TIME_SD"):
        config[c] = float(config[c])

    config["MQTT_TOPIC_PUB"] = config["MQTT_TOPIC_PUB"] + "/" + config["HOSTNAME"]

    publisher = MyMQTTPublisher(
        topic=config["MQTT_TOPIC_PUB"],
        sleep_time=config["SLEEP_TIME"],
        sleep_time_sd=config["SLEEP_TIME_SD"]
    )

    publisher.connect()
    publisher.start_publishing()
