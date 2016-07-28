__author__ = 'davigar'

import threading
import time

from gateway.sensor import Sensor, SAction, SSetting
from gateway.config import config
from gateway.sensorlogic import SensorLogic
from logic.grovepioperator import GrovePiOperator


relay = Sensor('relay', 'relay_1', 'RRelay')

on_action = SAction('on')
off_action = SAction('off')
flash_action = SAction('flash')

duration_setting = SSetting('duration', 0, [2, 100], 10, True)
interval_setting = SSetting('interval', 0, [0.1, 10], 1, True)
flash_action.add_setting(duration_setting)
flash_action.add_setting(interval_setting)

relay.add_action(on_action)
relay.add_action(off_action)
relay.add_action(flash_action)


class RelayLogic(SensorLogic):
    state = 0
    duration = 10
    interval = 1
    t = None

    @staticmethod
    def action(sensor, action):
        pin = config['sensors'][sensor.id]['pin']
        if action.name == 'on':
            RelayLogic.do_on(pin)
        elif action.name == 'off':
            RelayLogic.do_off(pin)
        elif action.name == 'flash':
            RelayLogic.do_flash(action.parameters, pin)
        else:
            pass

    @staticmethod
    def write(data, pin):
        GrovePiOperator.write(pin, data)

    @staticmethod
    def do_on(pin):
        RelayLogic.write(1, pin)
        RelayLogic.state = 1

    @staticmethod
    def do_off(pin):
        RelayLogic.write(0, pin)
        RelayLogic.state = 0

    @staticmethod
    def do_flash(parameters, pin):
        if parameters is not None:
            for parameter in parameters:
                if parameter.name == 'duration':
                    RelayLogic.duration = int(parameter.value)
                elif parameter.name == 'interval':
                    RelayLogic.interval = float(parameter.value)
                else:
                    pass

        if RelayLogic.state == 2:
            return
        RelayLogic.state = 2

        RelayLogic.t = threading.Thread(target=RelayLogic.flash, args=(pin,))
        RelayLogic.t.daemon = True
        RelayLogic.t.start()

    @staticmethod
    def flash(pin):
        write_key = 0
        while (RelayLogic.state == 2) and (RelayLogic.duration > 0):
            RelayLogic.write(write_key, pin)
            if write_key == 0:
                write_key = 1
            else:
                write_key = 0
            time.sleep(RelayLogic.interval)
            RelayLogic.duration -= RelayLogic.interval
        if RelayLogic.state == 2:
            RelayLogic.write(0, pin)
            RelayLogic.state = 0
        else:
            RelayLogic.write(RelayLogic.state, pin)
        # resume
        RelayLogic.duration = 10
        RelayLogic.interval = 1
