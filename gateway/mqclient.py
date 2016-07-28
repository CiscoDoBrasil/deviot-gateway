__author__ = 'tingxxu'

import paho.mqtt.client as mqtt
import sys
from gateway.sensor import *
import json
import time
default_user = "guest"


class MQClient:

    def __init__(self, data_topic, action_topic):
        self.__sender = mqtt.Client()

        self.__sender.on_connect = self.__on_connect
        self.__sender.on_message = self.__on_message

        self.__data_topic = data_topic
        self.__action_topic = action_topic

    def __on_connect(self, client, userdata, flags, rc):
        self.__sender.subscribe(self.__action_topic)
        self.print_status()

    # The callback for when a PUBLISH message is received from the server.
    def __on_message(self, client, userdata, msg):

        message = str(msg.payload)
        data = json.loads(message)
        print(msg.topic+" "+str(msg.payload))
        try:
            sensor_id = data["name"]

            action = SAction(data['action'])
            for key in data:
                if key != "name" and key != "action":
                    setting = SSetting(key, 0, [0, 100], data[key], True)
                    action.add_setting(setting)
            try:
                self.manager.action(default_user, sensor_id, action)
                res = "{\"result\":\"%s\"}" % "ok"
                print(res)
            except:
                res = "{\"result\":\"%s\"}" % sys.exc_info()[1]
                print(res)
        except:
             print("the data from server ")

    def run(self, server_host, server_port):
        self.__sender.connect(server_host,server_port, 60)
        self.__sender.loop_start()
        while True:
            data = self.manager.get_sensors_data(default_user, None)
            self.__sender.publish(self.__data_topic, data)
            time.sleep(0.2)

    def print_status(self):
        print("##########################################################")
        print("#                                                        #")
        print("#        Gateway Service Started Successfully            #")
        print("#                                                        #")
        print("##########################################################")