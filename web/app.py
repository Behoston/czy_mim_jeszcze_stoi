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
    last_checks = fill_gaps(last_checks)
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
    results = []
    cursor = get_db().cursor()
    cursor.execute(
        'SELECT timestamp, mail, lab, usos, ssh '
        'FROM status '
        'ORDER BY timestamp DESC',
    )
    for status in cursor.fetchmany(how_many):
        results.append(models.Status(status[0], *[bool(e) for e in status[1:]]))
    results.reverse()
    return results


def fill_gaps(statuses: [models.Status], how_long: int = 100) -> [models.Status]:
    filled = []
    refresh_seconds = int(config.REFRESH_TIME.total_seconds())
    after = int(time.time()) - refresh_seconds * how_long
    first_status_index = 0
    for i, status in enumerate(statuses):
        if status.timestamp < after:
            first_status_index = i
        else:
            break
    statuses = statuses[first_status_index:]
    if after - statuses[0].timestamp > refresh_seconds / 2:
        statuses[0] = copy_with_new_timestamp(statuses[0], after)
    while statuses:
        filled.append(statuses.pop(0))
        if not statuses:
            while len(filled) != how_long:
                filled.append(copy_with_new_timestamp(filled[-1], filled[-1].timestamp + refresh_seconds))
        else:
            while statuses[0].timestamp - filled[-1].timestamp > refresh_seconds:
                filled.append(copy_with_new_timestamp(filled[-1], filled[-1].timestamp + refresh_seconds))
    return filled


def copy_with_new_timestamp(status: models.Status, timestamp: int) -> models.Status:
    return models.Status(
        timestamp=timestamp,
        mail=status.mail,
        lab=status.lab,
        usos=status.usos,
        ssh=status.ssh,
    )


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
