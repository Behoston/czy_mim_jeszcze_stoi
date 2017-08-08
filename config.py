import getpass

PESEL = input('Podaj swój PESEL: ')
USERNAME = input('Podaj nazwę użytkownika: ')
PASSWORD = getpass.getpass(prompt='Podaj hasło do students: ')
CHECK_INTERVAL_SECONDS = 5 * 60
