__author__ = 'tingxxu'

from gateway.sensor import Sensor, SProperty
from gateway.config import config
from gateway.sensorlogic import SensorLogic
from logic.grovepioperator import GrovePiOperator


button = Sensor('button', 'button_r', 'RButton')

value_property = SProperty('pressed', 0, None, 0)

button.add_property(value_property)


class ButtonLogic(SensorLogic):

    @staticmethod
    def update(sensor, data):
        pin = config['sensors'][sensor.id]['pin']

        new_value = GrovePiOperator.read(pin)

        if 0 < new_value < 1024:
            updated_properties = {'pressed': 1}
        else:
            updated_properties = {'pressed': 0}
        SensorLogic.update_properties(sensor, updated_properties)
