import unittest

from backend.services.models import SourceStatus
from backend.services.search import SourceResult, search_jobs
from backend.tests.fixtures import BASE_PREFERENCES, FIXTURE_RESUME, MATCHING_JOB, STRETCH_JOB


class SearchAggregationTest(unittest.TestCase):
    def test_aggregates_filters_deduplicates_and_ranks_jobs(self):
        def fixture_source(_preferences):
            return SourceResult('fixture', [STRETCH_JOB, MATCHING_JOB, MATCHING_JOB], SourceStatus('fixture', 'available', 'ok'))

        response = search_jobs(FIXTURE_RESUME, BASE_PREFERENCES, sources=[fixture_source])

        self.assertEqual(len(response.results), 2)
        self.assertEqual(response.results[0].job.id, MATCHING_JOB.id)
        self.assertGreater(response.results[0].evaluation.score, response.results[1].evaluation.score)
        self.assertEqual(response.source_statuses[0].status, 'available')

    def test_returns_partial_results_when_one_source_fails(self):
        def ok_source(_preferences):
            return SourceResult('fixture', [MATCHING_JOB], SourceStatus('fixture', 'available', 'ok'))

        def failing_source(_preferences):
            raise RuntimeError('rate limited')

        response = search_jobs(FIXTURE_RESUME, BASE_PREFERENCES, sources=[ok_source, failing_source])

        self.assertEqual(len(response.results), 1)
        self.assertTrue(any(status.status == 'degraded' for status in response.source_statuses))


if __name__ == '__main__':
    unittest.main()
