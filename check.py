import collections
import poplib
import time

import paramiko
import requests

from config import PESEL, USERNAME, PASSWORD, CHECK_INTERVAL_SECONDS


def check_mail() -> bool:
    try:
        mServer = poplib.POP3_SSL('students.mimuw.edu.pl')
        mServer.user(USERNAME)
        mServer.pass_(PASSWORD)
        mServer.stat()
        mServer.quit()
        return True
    except:
        return False


def check_lk() -> bool:
    try:
        response = requests.get('http://lk.mimuw.edu.pl/')
        assert response.status_code == 200
        return True
    except:
        return False


def check_ssh() -> bool:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname='students.mimuw.edu.pl',
            username=USERNAME,
            password=PASSWORD,
        )
        return True
    except:
        return False


def check_usos() -> bool:
    try:
        url = 'https://logowanie.uw.edu.pl/cas/login'
        data = {
            'username': PESEL,
            'password': PASSWORD,
            'execution': 'e1s1',
            '_eventId': 'submit',
            'submit': 'ZALOGUJ',
        }
        response = requests.post(url, data)
        assert response.status_code == 200
        return True
    except:
        return False


Status = collections.namedtuple(
    'Status',
    ['timestamp', 'mail', 'lab', 'usos', 'ssh'],
)


def is_different(status_1: Status, status_2: Status) -> bool:
    return status_1[1:] != status_2[1:]


def get_status() -> Status:
    timestamp = int(time.time())
    mail = check_mail()
    lab = check_lk()
    usos = check_usos()
    ssh = check_ssh()
    return Status(timestamp, mail, lab, usos, ssh)


last_status = get_status()
while True:
    time.sleep(CHECK_INTERVAL_SECONDS)
    actual_status = get_status()
    print(actual_status)
    print('Changed?', is_different(actual_status, last_status))
    last_status = actual_status
