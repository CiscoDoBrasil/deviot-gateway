__author__ = 'davigar'

from gateway.sensor import Sensor
from gateway.sproperty import SProperty
from gateway.config import config
from gateway.sensorlogic import SensorLogic
from logic.grovepioperator import GrovePiOperator


rotary = Sensor('rotary', 'rotary_1', 'RRotary')

value_property = SProperty('angle', 0, [0, 100], 0)

rotary.add_property(value_property)


class RotaryLogic(SensorLogic):

    @staticmethod
    def update(sensor, data):
        pin = config['sensors'][sensor.id]['pin']
        new_value = GrovePiOperator.read(pin)
        if new_value is not None:
            updated_properties = {'angle': new_value}
        else:
            updated_properties = {}
        SensorLogic.update_properties(sensor, updated_properties)
