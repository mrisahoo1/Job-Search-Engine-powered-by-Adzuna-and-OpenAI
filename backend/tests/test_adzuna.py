import os
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import backend.services.sources as sources
from backend.services.models import SearchPreference
from backend.services.sources import build_adzuna_url, fetch_adzuna


def adzuna_item(identifier: str, title: str = 'Software Engineer'):
    return {
        'id': identifier,
        'title': title,
        'company': {'display_name': 'Leidos'},
        'location': {'display_name': 'Farnborough, Hampshire', 'area': ['UK', 'South East England', 'Hampshire']},
        'description': 'Software engineering role with APIs and delivery ownership.',
        'redirect_url': f'https://adzuna.example/{identifier}',
        'created': '2026-05-12T00:00:00Z',
    }


class AdzunaConnectorTest(unittest.TestCase):
    def test_builds_country_specific_adzuna_url(self):
        preferences = SearchPreference(query='backend engineer', region='eu_uk', countries=['United Kingdom'])

        url = build_adzuna_url(preferences, app_id='APPID', app_key='APPKEY')
        params = parse_qs(urlparse(url).query)

        self.assertIn('https://api.adzuna.com/v1/api/jobs/gb/search/1', url)
        self.assertEqual(params['app_id'], ['APPID'])
        self.assertEqual(params['app_key'], ['APPKEY'])
        self.assertEqual(params['what'], ['backend engineer'])
        self.assertEqual(params['results_per_page'], ['50'])

    def test_can_build_later_adzuna_pages(self):
        preferences = SearchPreference(query='product manager', region='india', countries=['India'])

        url = build_adzuna_url(preferences, app_id='APPID', app_key='APPKEY', page=3, results_per_page=25)

        self.assertIn('/jobs/in/search/3', url)
        self.assertEqual(parse_qs(urlparse(url).query)['results_per_page'], ['25'])

    def test_fetch_adzuna_paginates_until_configured_result_count(self):
        preferences = SearchPreference(query='software engineer', region='eu_uk', countries=['United Kingdom'])
        calls = []

        def fake_read_json(url: str):
            calls.append(url)
            page = int(urlparse(url).path.rsplit('/', 1)[-1])
            if page == 1:
                return {'count': 3, 'results': [adzuna_item('1'), adzuna_item('2', 'Lead Software Engineer')]}
            if page == 2:
                return {'count': 3, 'results': [adzuna_item('3', 'Platform Software Engineer')]}
            return {'count': 3, 'results': []}

        with patch.dict(os.environ, {'ADZUNA_APP_ID': 'APPID', 'ADZUNA_APP_KEY': 'APPKEY', 'ADZUNA_RESULTS_PER_PAGE': '2', 'ADZUNA_MAX_RESULTS': '3'}):
            with patch.object(sources, '_read_json', side_effect=fake_read_json):
                result = fetch_adzuna(preferences)

        self.assertEqual(len(result.jobs), 3)
        self.assertEqual(len(calls), 2)
        self.assertIn('3 of 3', result.status.message)
        self.assertIn('2 pages', result.status.message)

    def test_fetch_adzuna_reports_one_page_when_cap_met_on_first_page(self):
        preferences = SearchPreference(query='software engineer', region='eu_uk', countries=['United Kingdom'])

        with patch.dict(os.environ, {'ADZUNA_APP_ID': 'APPID', 'ADZUNA_APP_KEY': 'APPKEY', 'ADZUNA_RESULTS_PER_PAGE': '50', 'ADZUNA_MAX_RESULTS': '50'}):
            with patch.object(sources, '_read_json', return_value={'count': 10080, 'results': [adzuna_item(str(index)) for index in range(50)]}):
                result = fetch_adzuna(preferences)

        self.assertEqual(len(result.jobs), 50)
        self.assertIn('1 pages', result.status.message)

    def test_fetch_adzuna_returns_partial_results_when_later_page_fails(self):
        preferences = SearchPreference(query='software engineer', region='eu_uk', countries=['United Kingdom'])

        def fake_read_json(url: str):
            page = int(urlparse(url).path.rsplit('/', 1)[-1])
            if page == 1:
                return {'count': 4, 'results': [adzuna_item('1'), adzuna_item('2')]}
            raise RuntimeError('Adzuna page failed')

        with patch.dict(os.environ, {'ADZUNA_APP_ID': 'APPID', 'ADZUNA_APP_KEY': 'APPKEY', 'ADZUNA_RESULTS_PER_PAGE': '2', 'ADZUNA_MAX_RESULTS': '4'}):
            with patch.object(sources, '_read_json', side_effect=fake_read_json):
                result = fetch_adzuna(preferences)

        self.assertEqual(result.status.status, 'degraded')
        self.assertEqual(len(result.jobs), 2)
        self.assertIn('before page 2 failed', result.status.message)


if __name__ == '__main__':
    unittest.main()
