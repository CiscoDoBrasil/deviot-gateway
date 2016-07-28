__author__ = 'tingxxu'
__copyright__ = "2015 Cisco Systems, Inc."

import sys
import urlparse
from flask import Flask, jsonify, Response, request, abort, render_template
from saction import SAction, SSetting

# create simple flask server
flaskInstance = Flask(__name__)
flaskInstance.is_virtual = True
default_user = "guest"

# default handler
@flaskInstance.errorhandler(404)
def not_found(error):
    response = jsonify({'error': error.description})
    return response

@flaskInstance.route('/')
def index():
    return render_template('index.html', ip=flaskInstance.server_host, port=flaskInstance.port)


# get all clients from cmx
@flaskInstance.route('/api/<string:owner>/data', methods=['GET'])
def get_data(owner):
    sensors = request.args.getlist('name')
    user = get_user(owner)
    data = flaskInstance.manager.get_sensors_data(user, sensors)
    if data is not None:
        response = Response(response=data, status=200, mimetype="application/json")
    else:
        response = jsonify({'error': "Can't get the sensors"})
    return response

# get all clients from cmx
@flaskInstance.route('/api/data', methods=['GET'])
def get_default_data():
    return get_data(default_user)

@flaskInstance.route('/api/<string:owner>/action', methods=['POST', 'PUT'])
def activate_data(owner):
    print("post data is %s", request.query_string)
    if request.query_string is None:
        abort(400)

    user = get_user(owner)

    data = urlparse.parse_qs(request.query_string)
    sensor_id = data["name"][0]

    action = SAction(data['action'][0])
    for key in data:
        if key != "name" and key != "action":
            setting = SSetting(key, 0, [0, 100], data[key][0], True)
            action.add_setting(setting)
    try:
        flaskInstance.manager.action(user, sensor_id, action)
        res = "{\"result\":\"%s\"}" % "ok"
        response = Response(response=res, status=200, mimetype="application/json")
    except:
        res = "{\"result\":\"%s\"}" % sys.exc_info()[1]
        response = Response(response=res, status=400, mimetype="application/json")

    return response

@flaskInstance.route('/api/action', methods=['POST', 'PUT'])
def activate_default_data():
    return activate_data(default_user)

@flaskInstance.route('/api/<string:owner>/modify', methods=['POST', 'PUT'])
def modify_data(owner):
    user = get_user(owner)
    post_data = request.json
    if isinstance(post_data, dict):
        datas = []
        datas.append(post_data)
        result = flaskInstance.manager.modify(user, datas)
    else:
        result = flaskInstance.manager.modify(user, post_data)
    if result:
        response = Response(response={}, status=200, mimetype="application/json")
    else:
        response = Response(response={}, status=404, mimetype="application/json")
    return response

@flaskInstance.route('/api/modify', methods=['POST', 'PUT'])
def modify_default_data():
    return modify_data(default_user)


@flaskInstance.route('/api/subscribe', methods=['POST', 'PUT'])
def subscribe_data():
    flaskInstance.manager.notification(request.json["notifications"])
    return Response(response={}, status=200, mimetype="application/json")


def get_user(owner):
    if flaskInstance.is_virtual:
        return owner
    return default_user
