#!/usr/bin/env python

from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    @task(1)
    def model_selection(self):
        self.client.get("/treatment/200")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
