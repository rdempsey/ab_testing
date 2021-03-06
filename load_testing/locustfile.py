#!/usr/bin/env python

from locust import HttpLocust, TaskSet, task
from random import randint


class UserBehavior(TaskSet):
    @task(1)
    def model_selection(self):
        uid = randint(1, 4700)
        # upc_code = "%0.12d" % randint(0, 999999999999)
        self.client.get(f"/model/predict/{uid}")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
