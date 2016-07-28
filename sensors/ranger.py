__author__ = 'davigar'

import time

from gateway.sensor import Sensor
from gateway.sproperty import SProperty
from gateway.config import config
from gateway.sensorlogic import SensorLogic
from logic.grovepioperator import GrovePiOperator


ranger = Sensor('ranger', 'ranger_1', 'RRanger')

value_property = SProperty('distance', 0, [0, 100], 0)

ranger.add_property(value_property)


class RangerLogic(SensorLogic):

    @staticmethod
    def update(sensor, data):
        pin = config['sensors'][sensor.id]['pin']
        new_value = GrovePiOperator.read(pin, mode='ultrasonic')
        updated_properties = {'distance': new_value}
        SensorLogic.update_properties(sensor, updated_properties)
