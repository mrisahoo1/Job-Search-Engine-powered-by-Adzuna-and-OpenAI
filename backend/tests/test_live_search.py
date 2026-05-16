import unittest

from backend.services.models import JobPosting, SearchPreference, SourceStatus
from backend.services.search import SourceResult, search_jobs
from backend.tests.fixtures import FIXTURE_RESUME, MATCHING_JOB


class LiveSearchDedupeTest(unittest.TestCase):
    def test_live_search_deduplicates_across_sources(self):
        duplicate = JobPosting(id='official:duplicate', source_id='official', source_name='Official Careers', title=MATCHING_JOB.title, company=MATCHING_JOB.company, location=MATCHING_JOB.location, country=MATCHING_JOB.country, remote=MATCHING_JOB.remote, visa_sponsorship=MATCHING_JOB.visa_sponsorship, description=MATCHING_JOB.description, tags=MATCHING_JOB.tags, apply_url=MATCHING_JOB.apply_url, fetched_at=MATCHING_JOB.fetched_at, posted_at=MATCHING_JOB.posted_at)

        def first(_preferences):
            return SourceResult('source-a', [MATCHING_JOB], SourceStatus('source-a', 'available', 'ok'))

        def second(_preferences):
            return SourceResult('source-b', [duplicate], SourceStatus('source-b', 'available', 'ok'))

        response = search_jobs(FIXTURE_RESUME, SearchPreference(query='full stack engineer', region='eu_uk'), sources=[first, second])

        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].job.apply_url, MATCHING_JOB.apply_url)

    def test_live_search_deduplicates_same_role_location_even_with_different_urls(self):
        first_job = JobPosting(id='adzuna:1', source_id='adzuna', source_name='Adzuna', title='Software Engineer', company='Leidos', location='Fareham Common, Fareham', country='United Kingdom', remote='unknown', visa_sponsorship='unknown', description='Software engineering role with APIs.', tags=[], apply_url='https://adzuna.example/1', fetched_at=MATCHING_JOB.fetched_at, posted_at=MATCHING_JOB.posted_at)
        second_job = JobPosting(id='adzuna:2', source_id='adzuna', source_name='Adzuna', title='Software Engineer', company='Leidos', location='Fareham Common, Fareham', country='United Kingdom', remote='unknown', visa_sponsorship='unknown', description='Software engineering role with APIs.', tags=[], apply_url='https://adzuna.example/2', fetched_at=MATCHING_JOB.fetched_at, posted_at=MATCHING_JOB.posted_at)

        def source(_preferences):
            return SourceResult('adzuna', [first_job, second_job], SourceStatus('adzuna', 'available', 'ok'))

        response = search_jobs(FIXTURE_RESUME, SearchPreference(query='software engineer', region='eu_uk', sources=['adzuna'], search_mode='adzuna'), sources=[source])

        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].job.title, 'Software Engineer')


if __name__ == '__main__':
    unittest.main()
