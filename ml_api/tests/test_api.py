#!/usr/bin/env python

"""
Test the ML API.
Must have the API running in order for the tests to work.
"""

import requests
import pytest


BASE_URL = "http://localhost:5000"


@pytest.fixture()
def api_config():
    api_config = dict()
    with open('../api.env', 'r') as f:
        for line in f:
            x = [item.strip() for item in line.split("=")]
            api_config[x[0]] = x[1]
    return api_config


class TestMlAPI:

    def test_prediction_endpoint_returns_prediction_when_input_valid(self, api_config):
        """Ensure the prediction endpoint returns a prediction with proper input."""
        url = f"{BASE_URL}/{api_config['MODEL_NAME'].lower()}/predict/200"
        response = requests.get(url)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json['model_name'] == 'model'
        assert response_json['uid'] == "200"
        assert response_json['group_assignment'] in ['control', 'variation']
        assert type(response_json['prediction']) == float

    def test_prediction_endpoint_returns_404_without_args(self, api_config):
        """Ensure the prediction endpoint returns a 404 when no uid is provided."""
        url = f"{BASE_URL}/{api_config['MODEL_NAME'].lower()}/predict"
        response = requests.get(url)
        assert response.status_code == 404

    def test_health_endpoint(self):
        """Ensure the health endpoint returns a 200."""
        url = f"{BASE_URL}/health"
        response = requests.get(url)
        response_json = response.json()
        assert response.status_code == 200
        assert response_json['status'] == 200

    def test_readiness_endpoint(self):
        """Ensure the readiness endpoint returns a 503 when no model is loaded."""
        url = f'{BASE_URL}/ready'
        response = requests.get(url)
        response_json = response.json()
        assert response.status_code == 503
        assert response_json['status'] == 503
