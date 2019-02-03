# A/B Testing

This repo is a fully-featured proof-of-concept for creating an API endpoint for a machine learning model.

## Features

* A/B testing (control/variation)
* Load testing
* Caching of group assignments
* API and model metrics with visualization

## Introduction to A/B Testing

A/B testing, also known as split testing, is used to compare two versions of something to see which performs better. Typically used for testing two versions of landing or sales pages, we can use it to test different versions of machine learning (ML) models, or compare the results of an ML model to the current state of affairs.

A/B testing works as follows:

1. Select a control. The control is usually what is currently in place.
2. Create a variation.
3. As consumers are served either the control or variation, engagement is measured and collected.
4. Run the test until there is enough data to gain statistical significance.
5. End the test and analyze the results.

From a technical viewpoint, the testing flow looks like this:

1. Consumer hits an API end point.
2. Consumer is assigned to a group (control or variation).
3. API responds with the control or variation.
4. The results are stored in a data store.

To help ensure we can achieve statistical significance in an experiment we:

1. Evenly divide consumers into the two groups.
2. Keep API groups mutually exclusive.
3. Keep a consumer in their assigned group.

## Requirements

* Docker

## What's In The Box?

* [Flask](http://flask.pocoo.org/): a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
* [Gunicorn](https://gunicorn.org/): a Python WSGI HTTP Server for UNIX. All of the APIs run using gunicorn.
* [Locust](https://locust.io/): an open source load testing tool.
* [Redis](https://redis.io): for caching
* [Elasticsearch](https://www.elastic.co/products/elasticsearch): logs and metric storage
* [Logstash](https://www.elastic.co/products/logstash): transfers logs into Elasticsearch
* [Kibana](https://www.elastic.co/products/kibana): log and metric visualization
* [MySQL](https://www.mysql.com/): storing non-log data

The entire stack is run in [Docker](https://www.docker.com/) containers.

## Usage: Three Easy Steps!

1. Launch the stack: `docker-compose up --build --force-recreate -d`
2. Open your browser and go to the Locust UI at http://127.0.0.1:8089
3. Run your load tests.

## Usage for Real Life

1. Create a machine learning model with [scikit-learn](https://scikit-learn.org/stable/index.html) and save it to disk using [joblib](https://pypi.org/project/joblib/).
2. Update the `api.env` file in `ml_api/api.env` with the path to the model.
3. Add code to retrieve the features your model needs.
4. Launch the API.

If using a different model library, you can update the project to load pickled models instead.