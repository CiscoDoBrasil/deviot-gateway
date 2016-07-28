__author__ = 'tingxxu'

import os
import sys
import json
import threading
import time

from singleton import Singleton
from user import User
from sensor import Sensor, SProperty, SAction, SSetting
from sensorlogic import SensorLogic
from config import config


class SensorManager(Singleton):
    def __init__(self):
        Singleton.__init__(self)
        self.__models__ = {}
        self.__logic__ = {}
        self.__sensors__ = {}
        self.users = {}
        self.__notification_data__ = []
        self.__t__ = None

        self.default_sensor_logic = SensorLogic

    def load_sensor_model(self, sensor, logic):

        if sensor.kind not in self.__models__:
            self.__models__[sensor.kind] = sensor
            self.__logic__[sensor.kind] = logic

    def load_sensors(self):
        if "sensors" not in config:
            print("can not find the sensors segment in setting.cfg")
            return

        all_sensors = config["sensors"]
        for sensor_id in all_sensors:
            if sensor_id not in self.__sensors__:
                sensor_object = all_sensors[sensor_id]
                if "kind" in sensor_object:
                    sensor_object_kind = sensor_object["kind"]
                    if sensor_object_kind in self.__models__:
                        new_sensor = SensorLogic.copy_with_info(self.__models__[sensor_object_kind], sensor_id, sensor_object["name"])
                        self.__sensors__[sensor_id] = new_sensor
                    else:
                        new_sensor = Sensor(sensor_object_kind, sensor_id, sensor_object["name"])
                        if sensor_object["type"] is "action":
                            on_action = SAction("on")
                            off_action = SAction("off")
                            new_sensor.add_action(on_action)
                            new_sensor.add_action(off_action)
                        else:
                            value_property = SProperty("value", 0, None, 0)
                            new_sensor.add_property(value_property)
                        self.__sensors__[sensor_id] = new_sensor
                else:
                    print("{0:s} sensor in setting.cfg lost kind property".format(sensor_id))

    def contain(self, name):
        return name in self.__models__

    def update(self, data):

        for user_key in self.users:
            user = self.users[user_key]
            for sensor_key in user.sensors:
                try:
                    sensor = user.sensors[sensor_key]
                    if sensor.kind in self.__logic__:
                        self.__logic__[sensor.kind].update(sensor, data)
                    elif self.default_sensor_logic is not None:
                        self.default_sensor_logic.update(sensor, data)
                    else:
                        pass
                    time.sleep(0.2)
                except:
                    pass
                    # print("SensorManager error when update %s, the info is %s:" % (sensor_key, str(sys.exc_info()[1])))

    def begin_update(self):

        for name in self.users:
            user = self.users[name]
            try:
                for sensor_key in user.sensors:
                    sensor = user.sensors[sensor_key]
                    self.__logic__[sensor.kind].begin_update(sensor, None)
            except:
                print("sensor manager begin_update ", sys.exc_info()[1])

    def end_update(self, data):

        for name in self.users:
            user = self.users[name]
            try:
                for sensor_key in user.sensors:
                    sensor = user.sensors[sensor_key]
                    self.__logic__[sensor.kind].end_update(sensor, data)
            except:
                print(sys.exc_info()[1])

    def cache(self, data):
        for logic_key in self.__logic__:
            self.__logic__[logic_key].cache(data)

    def notification(self, data):
        self.__notification_data__.append(data)
        if self.__t__ is None:
            self.__t__ = threading.Thread(target=self.__notification_on_background)
            self.__t__.daemon = True
            self.__t__.start()

    def __notification_on_background(self):
        while True:
            if len(self.__notification_data__) > 0:
                data = self.__notification_data__.pop()
                try:
                    for user_key in self.users:
                        user = self.users[user_key]
                        for sensor_key in user.sensors:
                            try:
                                sensor = user.sensors[sensor_key]
                                self.__logic__[sensor.kind].notification(data, sensor)
                            except:
                                print("notification_on_background" + sys.exc_info()[1])
                except:
                    print("notification_on_background", sys.exc_info()[1])
            time.sleep(0.2)

    def modify(self, owner, data):
        if owner in self.users:
            user = self.users[owner]
            success = 0
            for data_item in data:
                for sensor_key in user.sensors:
                    sensor = user.sensors[sensor_key]
                    result = self.__logic__[sensor.kind].modify(data_item, sensor.model)
                    if result:
                        temp = success
                        success = temp + 1
            if success is len(data):
                return True
        return False

    def action(self, owner, sensor_id, action):
        if owner in self.users:
            user = self.users[owner]
            try:
                if sensor_id in user.sensors:
                    sensor = user.sensors[sensor_id]
                    self.__logic__[sensor.kind].action(sensor, action)
            except:
                print("sensor manager action ", sys.exc_info()[1])

    def get_sensors_data(self, owner, sensors_id):
        if owner in self.users:
            data = self.sensor_data_build(owner, sensors_id)
        else:
            new_user = User(owner)
            if self.__is_virtual__ is False:
                for sensor_key in self.__sensors__:
                    sensor = self.__sensors__[sensor_key]
                    new_user.sensors[sensor.id] = sensor

            self.users[owner] = new_user
            data = self.sensor_data_build(owner, sensors_id)
        return json.dumps(data)

    def get_all_expression(self):
        result = []
        for sensor_id in self.__sensors__:
            sensor = self.__sensors__[sensor_id]
            expression = SensorManager.__get_sensor_expression(sensor)
            result.append(expression)
        return result

    def sensor_data_build(self, owner, sensors_id):
        data = {}
        try:
            if sensors_id is not None and len(sensors_id) > 0:
                for sensor_id in sensors_id:

                    if sensor_id in self.users[owner].sensors:
                            sensor = self.users[owner].sensors[sensor_id]
                            data[sensor_id] = self.__get_sensor_value_expression(sensor)
                    else:
                        if self.__is_virtual__:
                            for model_key in self.__models__:
                                if sensor_id.startswith(model_key):
                                    new_sensor = self.__logic__[model_key].copy_with_key(sensor_id,
                                                                                         self.__models__[model_key])

                                    self.users[owner].sensors[sensor_id] = new_sensor

                                    data[sensor_id] = self.__get_sensor_value_expression(new_sensor)

            else:
                for sensor_key in self.users[owner].sensors:
                    sensor = self.users[owner].sensors[sensor_key]
                    data[sensor.id] = self.__get_sensor_value_expression(sensor)
        except:
            print("sensor manager sensor_data_build ", sys.exc_info()[1])
        return data

    def __get_sensor_value_expression(self, sensor):
        expression = {}

        for property_item in sensor.__properties__:
            expression[property_item.name] = property_item.value
        return expression

    @staticmethod
    def __get_sensor_expression(sensor):
        expression = {}
        expression["id"] = sensor.id
        expression["name"] = sensor.name
        expression["kind"] = sensor.kind
        expression["properties"] = []
        expression["actions"] = []
        expression["settings"] = []

        for property_item in sensor.__properties__:
            expression["properties"].append({
                "name": property_item.name,
                "type": property_item.type,
                "range": property_item.range,
                "value": property_item.value,
                "description": property_item.description
            })

        for action_item in sensor.__actions__:
            action = {}
            action["name"] = action_item.name
            action["parameters"] = []
            for parameter_item in action_item.parameters:
                parameter = {
                    "name": parameter_item.name,
                    "type": parameter_item.type,
                    "range": parameter_item.range,
                    "value": parameter_item.value,
                    "description": parameter_item.description,
                    "required": parameter_item.required
                }
                action["parameters"].append(parameter)

            expression["actions"].append(action)

        for setting_item in sensor.__settings__:
            expression["settings"].append({
                "name": setting_item.name,
                "type": setting_item.type,
                "range": setting_item.range,
                "value": setting_item.value,
                "description": setting_item.description,
                "required": setting_item.required
            })

        return expression

# -------------------------------------------------------------------------------- #

manager = SensorManager()


def import_sensors():
    current_folder = os.getcwd()
    sensors_folder = current_folder + "/sensors"
    sensor_files = os.listdir(sensors_folder)

    for sensor_file in sensor_files:
        if sensor_file.endswith('.py') and sensor_file.endswith('__.py') is False:
            sensor_info = sensor_file.split('.')
            sensor_name = sensor_info[0]
            sensor_logic = sensor_name[0].upper() + sensor_name[1:] +"Logic"
            if manager.contain(sensor_name) is False:
                import_sensor = "from sensors.{0:s} import {1:s}, {2:s}".format(sensor_name, sensor_name, sensor_logic)
                # import_sensor = "from sensors."+sensor_name +" import " + sensor_name +", "+ sensor_logic

                exec import_sensor
                add_sensor = "manager.load_sensor_model({0:s},{1:s})".format(sensor_name, sensor_logic)
                exec add_sensor

    manager.load_sensors()