#!/usr/bin/env python

from os import getenv
import logging
from flask import Flask
import ujson
import redis
import requests

app = Flask(__name__)

redis_host = getenv('REDIS_HOST', 'localhost')
redis_port = int(getenv('REDIS_PORT', 6379))
redis_db = int(getenv('REDIS_DB', 0))
ga_endpoint = getenv('GA_ENDPOINT', 'http://localhost:8000/group-assignment')

client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, charset="utf-8", decode_responses=True)


def _get_log_level():
    """Get the log level from the environment"""
    lvl = getenv('LOG_LEVEL', 'INFO')
    if lvl == 'DEBUG':
        return logging.DEBUG
    elif lvl == 'INFO':
        return logging.INFO
    elif lvl == 'WARNING':
        return logging.WARNING
    elif lvl == 'ERROR':
        return logging.ERROR
    elif lvl == 'CRITICAL':
        return logging.CRITICAL


logging.basicConfig(filename=getenv('LOG_FILE'), level=_get_log_level())
logger = logging.getLogger()


def _check_cache(store_number):
    """Check the Redis cache for the store number and return if found."""
    return client.get(store_number)


def _add_to_cache(store_number, group_assignment):
    """Add a store and group_assignment to the cache."""
    client.set(store_number, group_assignment)


@app.route("/ml/<int:store_number>")
def get_ml_model(store_number):
    group_assignment = _check_cache(store_number)

    if group_assignment is None:
        response = requests.get(f'{ga_endpoint}/{store_number}')
        data = response.json()
        group_assignment = data['group_assignment']
        _add_to_cache(store_number, group_assignment)

    response = {
        'store_number': store_number,
        'group_assignment': group_assignment
    }

    logger.info(response)

    return ujson.dumps(response)


if __name__ == "__main__":
    app.run()
