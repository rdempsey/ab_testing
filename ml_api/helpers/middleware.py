"""
middleware.py

Capture metrics on the response time of the api endpoints.
"""

from flask import request
import ujson
from datetime import datetime
import time
from os import getenv
from utils import utils


def start_timer():
    """ Start the request timer."""
    request.start_time = time.time()


def stop_timer(response):
    """Stop the timer and add to the metrics log."""
    metrics_log_file = getenv('METRICS_LOG_FILE', '../logs/ml_api/metrics.log')
    resp_time = (time.time() - request.start_time)*1000
    utc_now = datetime.utcnow()
    log_data = {
        'type': 'log',
        'written_at': utils.iso_time_format(utc_now),
        'written_ts': utils.epoch_nano_second(utc_now),
        'msg': 'ml_api.metric.response_time',
        'endpoint': request.endpoint,
        'response_time': str(resp_time)
    }
    with open(metrics_log_file, 'a') as outfile:
        outfile.write(ujson.dumps(log_data, outfile) + "\n")

    return response


def setup_metrics(app):
    """Set up the metrics on the request."""
    app.before_request(start_timer)
    app.after_request(stop_timer)
