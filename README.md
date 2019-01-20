# A/B Testing

This repo is a POC for developing, testing and load testing an A/B testing API.

## Requirements

* Python 3.7.x

## What's In The Box?

* [Falcon](https://falconframework.org/#): a bare-metal Python web API framework for building very fast app backends and microservices.
* [Gunicorn](https://gunicorn.org/): a Python WSGI HTTP Server for UNIX.
* [Locust](https://locust.io/): an open source load testing tool.


## Installation

1. Install Python with [Anaconda](https://www.anaconda.com/download/).
2. Create and activate a new Anaconda 3.7 environment: `conda create --name py37 python=3.7`
3. [Clone the Github repo](https://github.com/rdempsey/ab_testing) and cd into the directory.
4. Install the Python libraries: `pip install -r requirements.txt`
5. Install Falcon and ensure it compiles with Cython: `pip install -v --no-binary :all: falcon`


## Usage

For ease of use, there are shell scripts that will launch the API and Locust with default parameters. Change them to suit your needs, specifically the $PATH variable as I have hard-coded the path to my Conda environment.

First, launch the API:

```
cd api
./run_ab_endpoint.sh
```

Next, launch Locust:

```
cd load_testing
./run_locust.sh
```

Finally, launch your browser and go to http://127.0.0.1:8089/, and run your load tests.