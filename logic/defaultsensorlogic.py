__author__ = 'tingxxu'

from gateway.config import config
from gateway.sensorlogic import SensorLogic
from grovepioperator import GrovePiOperator


class DefaultSensorLogic(SensorLogic):

    @staticmethod
    def update(sensor, data):
        pin = config["sensors"][sensor.id]['pin']
        new_value = GrovePiOperator.read(pin)
        updated_properties = {"value": new_value}
        SensorLogic.update_properties(sensor, updated_properties)

    @staticmethod
    def action(sensor, action):
        pin = config["sensors"][sensor.id]['pin']
        if action.name == 'on':
            GrovePiOperator.write(pin, 1)
        elif action.name == 'off':
            GrovePiOperator.write(pin, 0)
        else:
            pass