#!/usr/bin/env python

from os import getenv
import json_logging
import logging
from flask import Flask
import ujson

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

logger = logging.getLogger("experiments_api_logger")
logger.setLevel(_get_log_level())
logger.addHandler(logging.FileHandler(filename=getenv('LOG_FILE', 'ml_admin.log')))

# MySQL


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


@app.route("/")
def say_hello():
    response = {
        'message': "Hello!"
    }

    _create_log("DSIM model served", response)

    return ujson.dumps(response)


if __name__ == "__main__":
    app.run()
