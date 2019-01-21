#!/usr/bin/env python

import logging
from flask import Flask, jsonify
import redis
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
client = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)


def _check_cache(store_number):
    """Check the Redis cache for the store number and return if found."""
    return client.get(store_number)


def _add_to_cache(store_number, treatment):
    """Add a store and treatment to the cache. All keys expire within 5 minutes."""
    client.set(store_number, treatment, ex=5*60)


@app.route("/ml/<int:store_number>")
def get_ml_model(store_number):
    group_assignment = _check_cache(store_number)

    if group_assignment is None:
        response = requests.get(f'http://localhost:8000/group-assignment/{store_number}')
        data = response.json()
        group_assignment = data['group_assignment']
        _add_to_cache(store_number, group_assignment)

    response = {
        'store_number': store_number,
        'group_assignment': str(group_assignment)
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(server='tornado')
