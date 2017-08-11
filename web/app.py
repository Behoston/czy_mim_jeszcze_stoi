import sqlite3
import time

import flask
from flask import g

import config
import models

app = flask.Flask('status')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s)


@app.route('/')
def status_page():
    last_checks = get_last_checks()
    fully_operational = is_fully_operational(last_checks[-1])
    return flask.render_template('index.html',
                                 statuses=last_checks,
                                 fully_operational=fully_operational,
                                 )


def is_fully_operational(status: models.Status) -> bool or None:
    if not all(status[1:]):
        if any(status[1:]):
            return None
        else:
            return False
    else:
        return True


def get_last_checks(how_many: int = 100) -> [models.Status]:
    return [get_random_status() for _ in range(how_many)]
    results = []
    cursor = get_db().cursor()
    after = int(time.time()) - int(config.REFRESH_TIME.total_seconds()) * how_many
    cursor.execute(
        'SELECT timestamp, mail, lab, usos, ssh '
        'FROM status '
        'WHERE timestamp > ? '
        'ORDER BY timestamp DESC',
        [after],
    )
    for status in cursor.fetchmany(how_many):
        results.append(models.Status(*status))
    return results


def get_last_status() -> models.Status:
    cursor = get_db().cursor()
    cursor.execute('SELECT * FROM status ORDER BY timestamp DESC LIMIT 1')
    last_status_tuple = cursor.fetchone()
    if not last_status_tuple:
        return
    else:
        return models.Status(*last_status_tuple)


def get_random_status() -> models.Status:
    import random
    return models.Status(
        timestamp=int(time.time()) - random.randint(0, 100000),
        mail=bool(random.getrandbits(1)),
        lab=bool(random.getrandbits(1)),
        usos=bool(random.getrandbits(1)),
        ssh=bool(random.getrandbits(1)),
    )


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
