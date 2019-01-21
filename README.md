# A/B Testing

This repo is a proof-of-concept for developing, testing and load testing an A/B testing API.

## Overview

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

* [Falcon](https://falconframework.org/#): a bare-metal Python web API framework for building very fast app backends and microservices.
* [Flask](http://flask.pocoo.org/): a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
* [Gunicorn](https://gunicorn.org/): a Python WSGI HTTP Server for UNIX. All of the APIs run using gunicorn.
* [Locust](https://locust.io/): an open source load testing tool.

The entire stack is run in [Docker](https://www.docker.com/) containers.

## Usage: Three Easy Steps!

1. Launch the stack: `docker-compose up --build --force-recreate -d`
2. Open your browser and go to the Locust UI at http://127.0.0.1:8089
3. Run your load tests.

## Internal Benchmarks

All benchmarks were run on my Mac (2.2 GHz Intel Core i7, 16 GB 1600 MHz DDR3) using Locust.

### Group Assignments Only

|Workers|Threads|Simultaneous Users|Hatch Rate|Run Time|Max Reqs/Sec|
|-------|-------|------------------|----------|--------|------------|
|10     |2      |300               |10        |5 min   |292.2       |
|10     |2      |300               |10        |5 min   |292.7       |
|10     |4      |300               |10        |5 min   |294.5       |
|12     |2      |300               |10        |5 min   |291.1       |
|9      |4      |300               |10        |5 min   |292.5       |
|10     |4      |300               |10        |5 min   |292         |


### Flask API w/ Redis Cache + Group Assignments (No Docker)

|Workers|Threads|Simultaneous Users|Hatch Rate|Run Time|Max Reqs/Sec|JSON Lib|
|-------|-------|------------------|----------|--------|------------|--------|
|9      |2      |5000              |50        |5 min   |477.1       |flask   |
|9      |2      |5000              |50        |2.5 min |526.1       |ujson   |

### The Full Monty in Docker

|Workers|Threads|Simultaneous Users|Hatch Rate|Run Time|Max Reqs/Sec|JSON Lib|
|-------|-------|------------------|----------|--------|------------|--------|
|9      |2      |5000              |50        |2.5 min |330.1       |ujson   |
