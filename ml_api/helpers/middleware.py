"""
middleware.py

Capture metrics on the response time of the api endpoints.
"""

from flask import request
import ujson
from datetime import datetime
import time
from os import getenv


metrics_log_file = getenv('METRICS_LOG_FILE', '../logs/ml_api/metrics.log')
_epoch = datetime(1970, 1, 1)


def iso_time_format(datetime_):
    return '%04d-%02d-%02dT%02d:%02d:%02d.%03dZ' % (
        datetime_.year, datetime_.month, datetime_.day, datetime_.hour, datetime_.minute, datetime_.second,
        int(datetime_.microsecond / 1000))


def epoch_nano_second(datetime_):
    return int((datetime_ - _epoch).total_seconds()) * 1000000000 + datetime_.microsecond * 1000


def start_timer():
    request.start_time = time.time()


def stop_timer(response):
    # convert this into milliseconds for statsd
    resp_time = (time.time() - request.start_time)*1000
    utc_now = datetime.utcnow()
    log_data = {
        'type': 'metric',
        'written_at': iso_time_format(utc_now),
        'written_ts': epoch_nano_second(utc_now),
        'msg': 'ml_api.metric.response_time',
        'session_id': request.cookies['sessionid'],
        'endpoint': request.endpoint,
        'response_time': str(resp_time)
    }
    with open(metrics_log_file, 'a') as outfile:
        outfile.write(ujson.dumps(log_data, outfile) + "\n")

    return response


def setup_metrics(app):
    app.before_request(start_timer)
    app.after_request(stop_timer)
