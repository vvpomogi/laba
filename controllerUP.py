import os
from threading import Thread
import subprocess
from dotenv import load_dotenv


load_dotenv('.env')


def wait_for_process(p):
    p.wait()


def thermometer(uuid):
    args = [r'emulator/temper/Temper', uuid, os.environ.get('CONTROLLER_SERVER_IP'), os.environ.get('FLASK_PORT')]
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL)
    t = Thread(target=wait_for_process, args=(p,))
    t.start()


def humidity(uuid):
    args = [r'emulator/humidity/Humid', uuid, os.environ.get('CONTROLLER_SERVER_IP'), os.environ.get('FLASK_PORT')]
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL)
    t = Thread(target=wait_for_process, args=(p,))
    t.start()


def light(uuid):
    args = [r'emulator/light/Light', uuid, os.environ.get('CONTROLLER_SERVER_IP'), os.environ.get('FLASK_PORT')]
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL)
    t = Thread(target=wait_for_process, args=(p,))
    t.start()


def CreateControllers(uuidList):
    for uuid in uuidList:
        if uuid[1] == 1:
            thermometer(uuid[0])
        elif uuid[1] == 2:
            light(uuid[0])
        elif uuid[1] == 3:
            humidity(uuid[0])
