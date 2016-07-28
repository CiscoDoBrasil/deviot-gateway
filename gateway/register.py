__author__ = 'tingxxu'

import threading
import json
import time
import sys

import httplib


class Register(threading.Thread):

    def __init__(self, name, manager, iot_address, server_ip, server_port, owner, is_mqtt=True, is_virtual=True):
        threading.Thread.__init__(self)
        self.__api_address__ = iot_address
        self.__ip__ = server_ip
        self.__port__ = server_port
        self.__manager__ = manager
        self.__app_name__ = name
        self.__is_virtual__ = is_virtual
        self.is_mqtt = is_mqtt
        self.__owner = owner

        self.MQData_topic = ("%s-%s-data" % (self.__app_name__, self.__owner)).encode('utf8')
        self.MQAction_topic = ("%s-%s-action" % (self.__app_name__, self.__owner)).encode('utf8')

    def run(self):
        api = "/api/v1/gateways"

        mode_value = 0
        if self.is_mqtt:
           mode_value = 2

        data = {}
        data['name'] = self.__app_name__
        data['mode'] = mode_value
        data['virtual'] = self.__is_virtual__
        data['host'] = self.__ip__
        data['port'] = self.__port__
        data['owner'] = self.__owner
        if self.is_mqtt is False:

            if self.__is_virtual__:
                data['data'] = '/api/{owner}/data'
                data['action'] = '/api/{owner}/action'
                data['setting'] = '/api/{owner}/modify'
            else:
                data['data'] = '/api/data'
                data['action'] = '/api/action'
                data['setting'] = '/api/modify'
        else:
            data['data'] = self.MQData_topic
            data['action'] = self.MQAction_topic
            data['setting'] = '/api/modify'

        data['sensors'] = self.__manager__.get_all_expression()

        json_data = json.dumps(data)

        while True:
            try:
                conn = httplib.HTTPConnection(self.__api_address__)
                conn.request("POST", api, json_data, {'Content-Type': 'application/json'})
                response = conn.getresponse()
            except IOError as e:
                print(e)
            except:
                print("--RunRegisterThread error:", sys.exc_info()[1])
            time.sleep(60)

    @staticmethod
    def adapter(sensor_model):
        return sensor_model
