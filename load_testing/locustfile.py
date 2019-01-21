#!/usr/bin/env python

from locust import HttpLocust, TaskSet, task
from random import randint


class UserBehavior(TaskSet):
    @task(1)
    def model_selection(self):
        self.client.get(f"/ml/{randint(1, 5000)}")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
