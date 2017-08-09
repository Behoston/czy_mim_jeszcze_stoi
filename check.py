import functools
import logging
import poplib
import time

import paramiko
import requests

import config
import database
import models

logger = logging.getLogger(__name__)
if config.DEBUG:
    logger.setLevel(level=logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)

DB = database.SQLite()


def check(fn) -> bool:
    @functools.wraps(fn)
    def wrapper():
        try:
            fn()
            return True
        except Exception as e:
            logger.warning(f'[{fn.__name__}]{e}')
            return False

    return wrapper


@check
def check_mail() -> bool:
    mServer = poplib.POP3_SSL('students.mimuw.edu.pl')
    mServer.user(config.USERNAME)
    mServer.pass_(config.PASSWORD)
    mServer.stat()
    mServer.quit()

@check
def check_lk() -> bool:
    response = requests.get('http://lk.mimuw.edu.pl/')
    assert response.status_code == 200


@check
def check_ssh() -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname='students.mimuw.edu.pl',
        username=config.USERNAME,
        password=config.PASSWORD,
    )


@check
def check_usos() -> bool:
    url = 'https://logowanie.uw.edu.pl/cas/login'
    data = {
        'username': config.PESEL,
        'password': config.PASSWORD,
        'execution': 'e1s1',
        '_eventId': 'submit',
        'submit': 'ZALOGUJ',
    }
    response = requests.post(url, data)
    assert response.status_code == 200


def is_different(status_1: models.Status, status_2: models.Status) -> bool:
    return status_1[1:] != status_2[1:]


def get_status() -> models.Status:
    timestamp = int(time.time())
    mail = check_mail()
    lab = check_lk()
    usos = check_usos()
    ssh = check_ssh()
    return models.Status(timestamp, mail, lab, usos, ssh)


DB.create_schema()
last_status = DB.get_last()
if last_status is None:
    last_status = get_status()
    DB.save(last_status)

while True:
    time.sleep(config.CHECK_INTERVAL_SECONDS)
    actual_status = get_status()
    if is_different(actual_status, last_status):
        DB.save(actual_status)
    last_status = actual_status
