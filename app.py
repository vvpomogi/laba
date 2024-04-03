import logging
import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from auth import auth as auth_blueprint
from main import main as main_blueprint
from controller import controller as controller_blueprint
from db import database as db, User, Controller
from controllerUP import CreateControllers


load_dotenv('.env')

app = Flask(__name__)


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(id=user_id)


app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(controller_blueprint)
app.secret_key = os.environ.get('SECRET_KEY')

controllers_list = []
controllers = Controller.select()
for controller in controllers:
    controllers_list.append((str(controller.id), controller.goods.id))
    logging.critical(controller)
CreateControllers(controllers_list)


if __name__ == '__main__':
    app.run(host=os.environ.get('FLASK_HOST'),
            port=os.environ.get('FLASK_PORT'),
            threaded=True)


