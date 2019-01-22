#!/usr/bin/env python

from os import getenv
import json_logging
import logging
from flask import Flask
import ujson
import redis
from hashlib import sha1

app = Flask(__name__)


# Logging
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


json_logging.ENABLE_JSON_LOGGING = True
json_logging.init(framework_name='flask')
json_logging.init_request_instrument(app)

logger = logging.getLogger("ml_api_logger")
logger.setLevel(_get_log_level())
logger.addHandler(logging.FileHandler(filename=getenv('LOG_FILE', 'api.log')))

# Redis
redis_host = getenv('REDIS_HOST', 'localhost')
redis_port = int(getenv('REDIS_PORT', 6379))
redis_db = int(getenv('REDIS_DB', 0))

client = redis.Redis(host=redis_host,
                     port=redis_port,
                     db=redis_db,
                     charset="utf-8",
                     decode_responses=True,
                     retry_on_timeout=True)


def _create_log(message, api_response):
    """Create a log in json format."""
    logger.info(message,
                extra={'props': {
                    'model_name': f"{api_response['model_name']}",
                    'store_number': f"{api_response['store_number']}",
                    'upc_code': f"{api_response['upc_code']}",
                    'group_assignment': f"{api_response['group_assignment']}",
                    'hash_key': f"{api_response['hash_key']}"
                }})


def _check_cache(hash_key):
    """Check the Redis cache for the store number and return if found."""
    return client.get(hash_key)


def _add_to_cache(hash_key, group_assignment):
    """Add a store and group_assignment to the cache."""
    client.set(hash_key, group_assignment)


def _deterministic_random_choice(hash_key, test_name, num_variations):
    """Returns a 'random'-ish number, between 0 and num_variations,
       based on the store_number and the test name.
       The number will not change if the store_number and test name
       remain the same.
    """
    return hash(str(hash_key) + test_name) % num_variations


def _get_group_assignment(hash_key, model_name):
    """Get the group assignment."""
    if _deterministic_random_choice(hash_key, model_name, 2) == 0:
        group_assignment = "control"
    else:
        group_assignment = "variation"
    return group_assignment


@app.route("/dsim/<int:store_number>/<int:upc_code>")
def serve_dsim_prediction(store_number, upc_code):
    model_name = "dsim"

    key_to_hash = f"{store_number}_{upc_code}".encode('utf-8')
    hash_key = sha1(key_to_hash).hexdigest()
    group_assignment = _check_cache(hash_key)

    if group_assignment is None:
        group_assignment = _get_group_assignment(hash_key, model_name)
        _add_to_cache(store_number, group_assignment)

    response = {
        'model_name': model_name,
        'store_number': store_number,
        'upc_code': upc_code,
        'group_assignment': group_assignment,
        'hash_key': hash_key
    }

    _create_log("DSIM model served", response)

    return ujson.dumps(response)


if __name__ == "__main__":
    app.run()
