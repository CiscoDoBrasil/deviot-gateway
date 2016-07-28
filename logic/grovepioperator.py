__author__ = 'tingxxu'

from gateway.pioperator import PiOperator

import os
import random

pi_operator = None

try:
    from grovepi import grovepi
    pi_operator = grovepi
except:
    try:
        import grovepi
        pi_operator = grovepi
    except:
        pi_operator = None

if pi_operator is None:
    print('Please install the grovepi first!')

analog = 'analog'
digital = 'digital'
input_fix = 'INPUT'
output_fix = 'OUTPUT'

is_debug = False
if 'DEBUG' in os.environ:
    is_debug = os.environ['DEBUG'] == 'TRUE'


class GrovePiOperator(PiOperator):

    @staticmethod
    def write(pin, data):
        if is_debug is False and pi_operator is not None:
            pi_operator.pinMode(pin, output_fix)
            pi_operator.digitalWrite(pin, data)
        else:
            print('write data...' + str(data))

    @staticmethod
    def read(pin, mode='analog'):
        if is_debug is False and pi_operator is not None:
            if mode is 'analog':
                data = pi_operator.analogRead(pin)
                if data > 1023:
                    return None
                return data
            elif mode == 'dht':
                temp, hum = pi_operator.dht(pin,0)
                return (temp, hum)
            elif mode == 'ultrasonic':
                distance = pi_operator.ultrasonicRead(pin)
                return distance
        else:
            return random.randint(0, 100)
