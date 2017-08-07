import getpass
import poplib

import paramiko
import requests

PESEL = input('Podaj swój PESEL: ')
USERNAME = input('Podaj nazwę użytkownika: ')
PASSWORD = getpass.getpass(prompt='Podaj hasło do students: ')


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


print('Strona labu działa? {}'.format(check_lk()))
print('Maile działają? {}'.format(check_mail()))
print('SSH działa? {}'.format(check_ssh()))
print('USOS działa? {}'.format(check_usos()))
