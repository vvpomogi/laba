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
import logging

main = Blueprint('main', __name__)


@main.route('/profile/', methods=['GET', 'POST', 'DELETE'])
def profile():
    if request.method == 'GET':
        groups = Group.select().where(Group.user_id == current_user.id)
        group_names = []
        for group in groups:
            group_names.append(group.name)

        group_name = str(request.args.get('selected_group'))
        if group_names:
            if not group_name in group_names:
                group_name = group_names[0]
        else:
            group_name = None
        selected_group = None
        group = Group.get_or_none(name=group_name, user=current_user.id)
        rows_controllers = []
        rows_grouped_controllers = []

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
                rows_controllers.append((controller.id, controller.goods.name))
        header1 = ("GUID", "Тип")
        groupData = {"groupName": " "}
        form = ControllersGroupForm(data=groupData)
        return render_template('profile.html', form=form, email=current_user.email,
                               rows=rows_controllers, rows1=rows_grouped_controllers, group_names=group_names,
                               header=header1, selected_group=selected_group)
    elif request.method == 'POST':
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
                    for id in ids:
                        Controller.update(group=group).where(Controller.id == id).execute()
        return redirect(url_for('main.profile'))
    elif request.method == 'DELETE':
        return 'OK', 200


@main.route('/profile/<uuid:id>', methods=['GET', 'DELETE', 'POST'])
def controller(id=None):
    if request.method == 'DELETE':
        Controller.delete_by_id(id)
        return 'OK', 200
    else:
        controller = Controller.get(Controller.id == id)
        settings = literal_eval(controller.settings)
        goods_id = controller.goods.id

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
        if goods_id == 1:
            form = ControllerThermometerForm(data=settings)
            fig = px.line(df, y="Показания", x="Время", title='Показания с контроллера')
        elif goods_id == 2:
            form = ControllerLightForm(data=settings)
            fig = px.line(df, y="Показания", x="Время", title='Показания с контроллера')
        elif goods_id == 3:
            form = ControllerHumidityForm(data=settings)
            fig = px.line(df, y="Показания", x="Время", title='Показания с контроллера')
        if form.validate_on_submit():
            settings = form.data
            del settings['submit']
            del settings['csrf_token']
            controller.settings = str(settings)
            controller.save()
            flash('<p class="notification is-warning">Запись успешно изменена</p>')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('edit.html', form=form, graphJSON=graphJSON)


@main.route('/profile/<int:gr_id>', methods=['DELETE'])
def group_delete(gr_id=None):
    controllers = Controller.select().where(Controller.group == gr_id)
    for controller in controllers:
        controller.update(group=None).execute()
    Group.delete_by_id(gr_id)
    return 'OK', 200


@main.route('/shop/')
@main.route('/shop/<int:id>')
@login_required
def shop(id=None):
    if not id:
        rows = []
        goods = Goods.select()
        for good in goods:
            rows.append((good.id, good.name))
        header = ("#", "Тип")
        return render_template('shop.html', rows=rows, header=header)
    else:
        guid = uuid.uuid4()
        user_id = current_user.id
        goods_id = id
        settings = ""
        if goods_id == 1:
            settings = "{'updateInterval': 10, 'temperatureHighLimit': 30, 'temperatureLowLimit': 22, 'criticalHighTemperature': 70, 'criticalLowTemperature': 0}"
        if goods_id == 2:
            settings = "{'updateInterval': 10, 'lightHighLimit': 70, 'lightLowLimit': 50}"
        if goods_id == 3:
            settings = "{'updateInterval': 10, 'humidityLowLimit': 70}"
        Controller.create(id=guid, user_id=user_id, goods_id=goods_id, group_id=None, settings=settings)
        flash('<p class="notification is-warning">Благодарим вас за покупку!</p>')
        controllersList = []
        controllersList.append([str(guid), goods_id])
        controllerUP.CreateControllers(controllersList)
        return redirect(url_for('main.shop'))


