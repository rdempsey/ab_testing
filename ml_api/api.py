#!/usr/bin/env python

from os import getenv
import json_logging
import logging
from flask import Flask, request
import ujson
import redis
from hashlib import sha1
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

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

logger = logging.getLogger(name=getenv('LOGGER_NAME', 'ml_api_logger'))
logger.setLevel(_get_log_level())
logger.addHandler(logging.FileHandler(filename=getenv('LOG_FILE', '/var/log/ml_api/ml_api.log')))

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

# Model Name for the main route
model_name = getenv("MODEL_NAME").lower()


def _create_log(message, log_extras):
    """Create a log in json format."""
    logger.info(message, extra={'props': log_extras})


def log_retry_redis(func, retry_num):
    """If a retry to Redis occurs, log it."""
    global logger
    if logger is not None:
        logger.info("ml_api_retry_redis",
                    extra={'props': {
                        'retry_num': retry_num
                    }})


@retry(
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
    retry=retry_if_exception_type(redis.ConnectionError),
    after=log_retry_redis
)
def _check_cache(hash_key):
    """Check the Redis cache for the store number and return if found."""
    return client.get(hash_key)


@retry(
    wait=wait_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
    retry=retry_if_exception_type(redis.ConnectionError),
    after=log_retry_redis
)
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


@app.route(f"/{model_name}/<int:store_number>/<int:upc_code>")
def serve_model_prediction(store_number, upc_code):
    key_to_hash = f"{store_number}".encode('utf-8')
    hash_key = sha1(key_to_hash).hexdigest()
    group_assignment = _check_cache(hash_key)

    if group_assignment is None:
        group_assignment = _get_group_assignment(hash_key, model_name)
        _add_to_cache(store_number, group_assignment)

    # TODO: Add ML action here
    prediction = None

    response = {
        'model_name': model_name,
        'store_number': store_number,
        'upc_code': upc_code,
        'group_assignment': group_assignment,
        'prediction': prediction
    }

    log_extras = {
        'model_name': model_name,
        'store_number': store_number,
        'upc_code': upc_code,
        'group_assignment': group_assignment,
        'hash_key': hash_key,
        'prediction': prediction,
        'request_url': request.url,
        'request_referrer': request.referrer
    }

    _create_log("ml_api_model_prediction_served", log_extras)

    return ujson.dumps(response)


if __name__ == "__main__":
    app.run()
