from ast import literal_eval
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import uuid
import controllerUP
from db import Controller, Group, Statistic, Goods
from forms import ControllerThermometerForm, ControllerHumidityForm, ControllerLightForm, ControllersGroupForm
import plotly
import plotly.express as px
import json
import pandas as pd

main = Blueprint('main', __name__)


@main.route('/profile/', methods=['GET'])
@login_required
def profile():
    group_name = str(request.args.get('selected_group'))
    if group_name == '':
        return redirect(url_for('main.profile'))
    groups = Group.select().where(Group.user_id == current_user.id)
    group_names = []
    for group in groups:
        group_names.append(group.name)
    selected_group = None
    rows_controllers = []
    rows_grouped_controllers = []
    group = Group.get_or_none(name=group_name, user=current_user.id)
    controllers = Controller.select().where(Controller.user == current_user.id)
    if group:
        selected_group = (group.id, group.name)
        for controller in controllers:
            if not controller.group:
                rows_controllers.append((controller.id, controller.goods.name))
            elif controller.group == group:
                rows_grouped_controllers.append((controller.id, controller.goods.name))
    else:
        for controller in controllers:
            if not controller.group:
                rows_controllers.append((controller.id, controller.goods.name))
    header1 = ("GUID", "Тип")
    groupData = {"groupName": " "}
    form = ControllersGroupForm(data=groupData)
    return render_template('profile.html', form=form, email=current_user.email,
                           rows=rows_controllers, rows1=rows_grouped_controllers, group_names=group_names,
                           header=header1, selected_group=selected_group)


@main.route('/profile/', methods=['POST'])
@login_required
def create_group():
    data = str(request.get_data())
    if not data == "b''":
        group_name = str(request.form['grouped'])
        if group_name == '':
            flash('<p class="notification is-danger">Название группы должно содержать хотя бы 1 символ</p>')
        else:
            group, _ = Group.get_or_create(name=group_name, user_id=current_user.id)
            rows = data.split('&')
            rows.pop(0)
            if rows:
                ids = []
                for row in rows:
                    ids.append(row[row.index('=') + 1:])
                ids[-1] = ids[-1][:-1]
                Controller.update(group=group).where(Controller.id.in_(ids)).execute()
    return redirect(url_for('main.profile'))


@main.route('/profile/<int:gr_id>', methods=['DELETE'])
@login_required
def delete_group(gr_id=None):
    Group.delete_by_id(gr_id)
    return 'OK', 200


def get_form(controller):
    goods_id = controller.goods.id
    settings = literal_eval(controller.settings)
    if goods_id == 1:
        form = ControllerThermometerForm(data=settings)
    elif goods_id == 2:
        form = ControllerLightForm(data=settings)
    elif goods_id == 3:
        form = ControllerHumidityForm(data=settings)
    else:
        form = None
    return form


@main.route('/profile/<uuid:id>', methods=['GET'])
@login_required
def get_sensor(id=None):
    controller = Controller.get_or_none(Controller.id == id)
    if controller:
        if request.method == 'GET':
            controller = Controller.get_or_none(Controller.id == id)
            statistics = Statistic.select().where(Statistic.controller_id == id).order_by(+Statistic.timing)
            if statistics:
                xlist = []
                ylist = []
                for statistic in statistics:
                    xlist.append(statistic.timing)
                    ylist.append(statistic.stats)
                df = pd.DataFrame({
                    "Показания": ylist,
                    "Время": xlist
                })
            form = get_form(controller)
            fig = px.line(df, y="Показания", x="Время", title='Показания с контроллера')
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('edit.html', form=form, graphJSON=graphJSON)


@main.route('/profile/<uuid:id>', methods=['POST'])
@login_required
def update_sensor(id=None):
    controller = Controller.get_or_none(Controller.id == id)
    form = get_form(controller)
    if form.validate_on_submit():
        settings = form.data
        del settings['submit']
        del settings['csrf_token']
        controller.settings = str(settings)
        controller.save()
        flash('<p class="notification is-warning">Запись успешно изменена</p>')
    return redirect(url_for('main.get_sensor', id=controller.id))


@main.route('/profile/<uuid:id>', methods=['DELETE'])
@login_required
def delete_sensor(id=None):
    Controller.delete_by_id(id)
    return 'OK', 200


@main.route('/shop/', methods=['GET'])
@login_required
def shop():
    rows = []
    goods = Goods.select()
    for good in goods:
        rows.append((good.id, good.name))
    header = ("#", "Тип")
    return render_template('shop.html', rows=rows, header=header)


@main.route('/shop/<int:id>', methods=['GET'])
@login_required
def buy_sensor(id=None):
    guid = uuid.uuid4()
    user_id = current_user.id
    goods_id = id
    settings = ""
    if goods_id == 1:
        settings = ("{'updateInterval': 10, 'temperatureHighLimit': 30, 'temperatureLowLimit': 22, "
                    "'criticalHighTemperature': 70, 'criticalLowTemperature': 0}")
    if goods_id == 2:
        settings = "{'updateInterval': 10, 'lightHighLimit': 70, 'lightLowLimit': 50}"
    if goods_id == 3:
        settings = "{'updateInterval': 10, 'humidityLowLimit': 70}"
    Controller.create(id=guid, user_id=user_id, goods_id=goods_id, group_id=None, settings=settings)
    flash('<p class="notification is-warning">Благодарим вас за покупку!</p>')
    controllersList = [[str(guid), goods_id]]
    controllerUP.CreateControllers(controllersList)
    return redirect(url_for('main.shop'))


