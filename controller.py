from ast import literal_eval
from flask import Blueprint, request, jsonify
from db import Controller, Statistic
import datetime

controller = Blueprint('controller', __name__)



@controller.route('/controller', methods=['POST'])
def controller_post():
    json_dict = request.get_json(force=True)
    guid = json_dict['guid']
    controller = Controller.get_or_none(Controller.id == guid)
    if controller:
        stats = json_dict['stats']
        timing = datetime.datetime.now()
        Statistic.create(controller=controller.id, stats=stats, timing=timing)

        user = controller.user
        number = user.number

        settings = literal_eval(controller.settings)
        if controller.goods == 1:
            settings['phoneNumber'] = number
        return jsonify(settings)
    else:
        return jsonify(None)
