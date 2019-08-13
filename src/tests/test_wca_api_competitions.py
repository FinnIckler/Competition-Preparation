import requests
import responses
import unittest
import json
from .test_constants import SAMPLE_COMPETITIONS
from lib.api.wca import get_upcoming_wca_competitions


class TestAPICompetitions(unittest.TestCase):
    # Some of these need to be mocked/run on integrating testing
    def setUp(self):
        # Auth always needs to be mocked
        def callback(request):
            # Mock a User that has no upcoming competitions
            if "Finn" in request.body:
                return (
                    200,
                    {},
                    json.dumps({"access_token": "Finn", "refresh_token": "bar"}),
                )
            else:
                return (
                    200,
                    {},
                    json.dumps({"access_token": "Leon", "refresh_token": "bar"}),
                )

        responses.add_callback(
            responses.POST,
            "https://www.worldcubeassociation.org/oauth/token",
            callback=callback,
            content_type="application/json",
        )

    @responses.activate
    def test_get_upcoming_wca_competitions(self):
        def callback(request):
            # Mock a User that has no upcoming competitions
            if "Finn" in request.headers["Authorization"]:
                return (200, {}, json.dumps([]))
            else:
                return (200, {}, json.dumps(SAMPLE_COMPETITIONS))

        responses.add_callback(
            responses.GET,
            "https://www.worldcubeassociation.org/api/v0/competitions",
            callback=callback,
            content_type="application/json",
        )
        self.assertEqual(
            get_upcoming_wca_competitions(password="hunter7", email="Finn@test.com"), []
        )
        self.assertEqual(
            get_upcoming_wca_competitions(password="hunter8", email="Leon@test.com"),
            SAMPLE_COMPETITIONS,
        )

    @responses.activate
    def test_get_wca_info(self):
        pass

    @responses.activate
    def test_get_wca_competition(self):
        pass
