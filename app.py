__author__ = 'tingxxu'

from gateway.service import Service
from gateway.config import config
from logic.defaultsensorlogic import DefaultSensorLogic

if __name__ == '__main__':

    devIot_address = config.get_string("address", "10.140.92.25:9000")
    mqtt_address = config.get_string("mqtthost", "10.140.92.25:1883")
    app_name = config.get_string("appname", "raspberry")
    communicator = config.get_string("communicator", "MQTT")
    devIot_account = config.get_info("account", "")

    app = Service(app_name, devIot_address, mqtt_address, devIot_account, communicator, False)
    app.default_sensor_logic = DefaultSensorLogic
    app.run()

