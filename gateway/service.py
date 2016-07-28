_author__ = 'tingxxu'


import time
import sys
import random

from threading import *

from listener import flaskInstance
from mqclient import MQClient
from register import Register
from singleton import Singleton
from datagetter import DataGetter

__main_manager__ = []


class RuImport(Thread):
    def __init__(self, main_thread_manager, is_virtual):
        Thread.__init__(self)
        self.main_thread_manager = main_thread_manager
        self.is_virtual = is_virtual

    def run(self):
        from sensormanager import manager, import_sensors
        manager.__is_virtual__ = self.is_virtual
        self.main_thread_manager.append(manager)
        while True:
            import_sensors()
            time.sleep(30)


class Service(Singleton):

    def __init__(self, app_name, iot_address, mqtt_address, deviot_account, communicator, is_virtual):

        self.app_name = app_name
        self.iot_address = iot_address
        self.communicator = communicator
        self.is_virtual = is_virtual
        self.deviot_account = deviot_account
        self.mqtt_address = mqtt_address

        self.default_sensor_logic = None

    def run(self):

        is_mqtt = self.communicator is not "HTTP"

        if is_mqtt is False:
            server_host = raw_input("--Please input local ip:\n")

            port = random.randint(5000, 5020)
            check = raw_input("--Would you like to use {0:d} as http server port, y or n?".format(port))
            if check.startswith('n'):
                is_ok = False
                while is_ok is False:
                    try:
                        port = int(raw_input("--Please input http server port number:\n"))
                        is_ok = True
                    except:
                        print("port number should be integer from 1000 to 9999")
                        is_ok = False
        else:
            try:
                mqtt_info = self.mqtt_address.split(":")
                server_host = mqtt_info[0]
                port = int(mqtt_info[1])
            except:
                print("the format of mqtt host should be: ip:port")
                return

        run_import = RuImport(__main_manager__, self.is_virtual)
        run_import.daemon = False
        run_import.start()
        print("being import sensors .......")
        time.sleep(5)

        __main_manager__[0].default_sensor_logic = self.default_sensor_logic

        register = Register(self.app_name, __main_manager__[0], self.iot_address, server_host,
                            port, self.deviot_account, is_mqtt, self.is_virtual)

        register.port = port
        register.start()

        getter = self.get_data_getter(server_host, port, __main_manager__[0])
        getter.start()

        if is_mqtt is False:
            print("being start http server at %d......." % port)
            flaskInstance.is_virtual = self.is_virtual
            flaskInstance.manager = __main_manager__[0]
            flaskInstance.port = port
            flaskInstance.server_host = server_host
            flaskInstance.run(debug=False, host=server_host, port=port)
        else:
            mqtt_listener = MQClient(register.MQData_topic, register.MQAction_topic)
            mqtt_listener.manager = __main_manager__[0]
            mqtt_listener.run(server_host, port)

        print('main thread finished!')

    def get_data_getter(self, ip, port, manager):
        # return a data getter
        getter = DataGetter(manager)
        return getter