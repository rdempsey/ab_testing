#!/usr/bin/env bash
export PATH="/anaconda3/envs/py37/bin:$PATH"
locust -f locustfile.py --host=http://localhost:8000