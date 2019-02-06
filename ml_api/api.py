#!/usr/bin/env python

"""
api.py

API to serve machine learning model predictions.
"""

from os import getenv
import json_logging
import logging
from flask import Flask, request
import ujson
import redis
from hashlib import sha1
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from time import time
from models.model import Model
from helpers.middleware import setup_metrics


app = Flask(__name__)
setup_metrics(app)


# Model
model_name = getenv("MODEL_NAME", "MODEL").lower()
model_file = getenv("MODEL_FILE_NAME", "model.joblib")
model = Model(model_file)


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
logger.addHandler(logging.FileHandler(filename=getenv('LOG_FILE', '../logs/ml_api/api.log')))


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


def _create_log(message, log_extras):
    """Create a log in json format."""
    logger.info(message, extra={'props': log_extras})


def log_retry_redis(func, retry_num):
    """If a retry to Redis occurs, log it."""
    global logger
    if logger is not None:
        logger.info("ml_api.retry_redis",
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


def _get_group_assignment(hash_key, ml_model_name):
    """Get the group assignment."""
    if _deterministic_random_choice(hash_key, ml_model_name, 2) == 0:
        group_assignment = "control"
    else:
        group_assignment = "variation"
    return group_assignment


@app.route('/health')
def health_check():
    """
    Health check endpoint.

    :return: 200 if the API is alive.
    """
    return ujson.dumps({"status": 200}), 200


@app.route('/ready')
def readiness_check():
    """
    Return the readiness of the model.

    :return: 200 if the model is ready, else 503
    """
    if model.is_ready():
        return ujson.dumps({"status": 200}), 200
    else:
        return ujson.dumps({"status": 503}), 503


@app.route(f"/{model_name}/predict/<string:uid>")
def serve_model_prediction(uid):
    """
    Prediction endpoint.

    :param uid: unique identifier to use for group assignment.
    :return: response: json containing the group assignment, model prediction and more.
    """
    key_to_hash = f"{uid}".encode('utf-8')
    hash_key = sha1(key_to_hash).hexdigest()
    group_assignment = _check_cache(hash_key)

    if group_assignment is None:
        group_assignment = _get_group_assignment(hash_key, model_name)
        _add_to_cache(uid, group_assignment)

    # Update the code below to retrieve the features your model needs and remove the hard coded prediction
    model_start = time()
    # features = list()
    # prediction = model.predict(features)
    prediction = 0.40
    model_end = time()

    response = {
        'model_name': model_name,
        'uid': uid,
        'group_assignment': group_assignment,
        'prediction': prediction
    }

    log_extras = {
        'endpoint': request.endpoint,
        'path': request.path,
        'url': request.url,
        'referrer': request.referrer,
        'uid': uid,
        'group_assignment': group_assignment,
        'hash_key': hash_key,
        'prediction': prediction,
        'model_name': model_name,
        'model_metadata': model.meta_data(),
        'model_request_duration': model_end - model_start
    }

    _create_log("ml_api.model_prediction_served", log_extras)

    return ujson.dumps(response), 200


if __name__ == "__main__":
    app.run()
