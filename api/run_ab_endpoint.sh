#!/usr/bin/env bash
export PATH="/anaconda3/envs/py37/bin:$PATH"
gunicorn -b 0.0.0.0:8000 --reload ab_endpoint:api --workers 10 --threads 2