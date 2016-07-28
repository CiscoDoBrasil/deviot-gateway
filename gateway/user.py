__author__ = 'tingxxu'


class User:

    def __init__(self, user_id):
        self.sensors = {}
        self.user_id = user_id

    def add_sensor(self, sensor):
        keys = self.sensors.keys()
        if sensor.key not in keys:
            self.sensors[sensor.key] = sensor
