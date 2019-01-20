#!/usr/bin/env python

"""
In thie api directory, run with this command:
  gunicorn -b 0.0.0.0:8000 --reload ab_endpoint:api --workers 10 --threads 2
"""

import logging
import falcon


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# falcon.API instances are callable WSGI apps
api = falcon.API()


class TreatmentsResource(object):
    def on_get(self, req, resp, store_number):
        """Handles GET requests"""
        treatment = self.final_experience(store_number)
        response = {
            'store_number': store_number,
            'treatment': treatment
        }

        resp.media = response
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200

    @staticmethod
    def _deterministic_random_choice(store_number, test_name, num_variations):
        """Returns a 'random'-ish number, between 0 and num_variations,
           based on the user_id and the test name.
           The number will not change if the user_id and test name
           remain the same.
        """
        return hash(str(store_number) + test_name) % num_variations

    def final_experience(self, store_number):
        if self._deterministic_random_choice(store_number, "model_test", 2) == 0:
            return "model_a"
        else:
            return "model_b"

# Resources and routes
treatments = TreatmentsResource()
api.add_route('/treatment/{store_number}', treatments)
