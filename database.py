import abc
import sqlite3

import models


class Backend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_schema(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, status: models.Status):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_last(self) -> models.Status:
        raise NotImplementedError()


class SQLite(Backend):
    def __init__(self):
        self.connection = sqlite3.connect('status.db')

    def create_schema(self):
        cursor = self.connection.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS status ('
            'timestamp INTEGER PRIMARY KEY, '
            'mail INTEGER, '
            'lab INTEGER, '
            'usos INTEGER, '
            'ssh INTEGER'
            ')'
        )
        cursor.execute('CREATE INDEX IF NOT EXISTS status_idx ON status (timestamp)')
        self.connection.commit()

    def save(self, status: models.Status):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO status VALUES (?,?,?,?,?)', status)
        self.connection.commit()

    def get_last(self) -> models.Status:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM status ORDER BY timestamp DESC LIMIT 1')
        last_status_tuple = cursor.fetchone()
        if not last_status_tuple:
            return
        else:
            return models.Status(*last_status_tuple)
