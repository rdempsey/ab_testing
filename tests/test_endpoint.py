#!/usr/bin/env python

import falcon
from falcon import testing
import pytest
from api.ab_endpoint import api


@pytest.fixture
def client():
    return testing.TestClient(api)


def test_get_treatment_for_store(client):
    response = client.simulate_get('/treatment/200')

    assert response.json['store_number'] == '200'
    assert response.json['treatment'] is not None
    assert response.status == falcon.HTTP_OK
