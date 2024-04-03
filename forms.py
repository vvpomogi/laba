from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, TextAreaField
from wtforms.fields import IntegerRangeField
from wtforms.validators import InputRequired, number_range


class ControllersGroupForm(FlaskForm):
    groupName = TextAreaField(u'Mailing Address', validators=[InputRequired()])


class ControllerThermometerForm(FlaskForm):
    updateInterval = IntegerField('Интервал обновления', validators=[InputRequired()])
    temperatureHighLimit = IntegerRangeField('Верхний предел', validators=[InputRequired()])
    temperatureLowLimit = IntegerRangeField('Нижний предел', validators=[InputRequired()])
    criticalHighTemperature = IntegerRangeField('Верхний предел для смс', validators=[InputRequired()])
    criticalLowTemperature = IntegerRangeField('Нижний предел для смс', validators=[InputRequired()])
    submit = SubmitField('Отправить')

    def validate_temperatureLowLimit(form, field):
        if field.data > form.temperatureHighLimit.data:
            field.data = form.temperatureHighLimit.data

    def validate_criticalLowTemperature(form, field):
        if field.data > form.criticalHighTemperature.data:
            field.data = form.criticalHighTemperature.data


class ControllerLightForm(FlaskForm):
    updateInterval = IntegerField('Интервал обновления', validators=[InputRequired()])
    lightHighLimit = IntegerRangeField(label='Верхний предел яркости', validators=[InputRequired(),
                                                                                   number_range(min=0, max=100,
                                                                                                message='Значение должно быть в диапазоне от 0 до 100')])
    lightLowLimit = IntegerRangeField(label='Нижний предел яркости', validators=[InputRequired(),
                                                                                 number_range(min=0, max=100,
                                                                                              message='Значение должно быть в диапазоне от 0 до 100')])
    submit = SubmitField('Отправить')

    def validate_lightLowLimit(form, field):
        if field.data > form.lightHighLimit.data:
            field.data = form.lightHighLimit.data


class ControllerHumidityForm(FlaskForm):
    updateInterval = IntegerField('Интервал обновления', validators=[InputRequired()])
    humidityLowLimit = IntegerRangeField('Поддерживаемый уровень влажности',
                                         validators=[InputRequired(), number_range(min=0, max=100,
                                                                                   message='Значение должно быть в диапазоне от 0 до 100')])
    submit = SubmitField('Отправить')
