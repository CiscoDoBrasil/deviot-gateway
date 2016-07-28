__author__ = 'davigar'

import time

from gateway.sensor import Sensor
from gateway.sproperty import SProperty
from gateway.config import config
from gateway.sensorlogic import SensorLogic
from logic.grovepioperator import GrovePiOperator


thermometer = Sensor('thermometer', 'thermometer_1', 'RThermometer')

temperature_property = SProperty('temperature', 0, [0, 100], 0)
humidity_property = SProperty('humidity', 0, [0, 100], 0)

thermometer.add_property(temperature_property)
thermometer.add_property(humidity_property)

class ThermometerLogic(SensorLogic):

    @staticmethod
    def update(sensor, data):
        pin = config['sensors'][sensor.id]['pin']
        new_temp, new_hum = GrovePiOperator.read(pin, mode='dht')
        updated_properties = {'temperature': new_temp, 'humidity': new_hum}
        SensorLogic.update_properties(sensor, updated_properties)
