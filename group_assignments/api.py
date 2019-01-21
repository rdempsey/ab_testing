#!/usr/bin/env python

import logging
import falcon


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GroupAssignmentResource(object):
    @staticmethod
    def _deterministic_random_choice(store_number, test_name, num_variations):
        """Returns a 'random'-ish number, between 0 and num_variations,
           based on the store_number and the test name.
           The number will not change if the store_number and test name
           remain the same.
        """
        return hash(str(store_number) + test_name) % num_variations

    def _get_group_assignment(self, store_number):
        """Get the group assignment."""
        if self._deterministic_random_choice(store_number, "model_test", 2) == 0:
            group_assignment = "control"
        else:
            group_assignment = "variation"
        return group_assignment

    def on_get(self, req, resp, store_number):
        """Handles GET requests"""
        group_assignment = self._get_group_assignment(store_number)

        response = {
            'store_number': store_number,
            'group_assignment': group_assignment,
        }

        resp.media = response
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200


# falcon.API instances are callable WSGI apps
api = falcon.API()

# Resources and routes
assignments = GroupAssignmentResource()
api.add_route('/group-assignment/{store_number}', assignments)
