import unittest
from unittest.mock import patch

from backend.services.models import SearchPreference
from backend.services.search import search_jobs
from backend.services.sources import (
    SourceResult,
    _extract_job_from_html,
    fetch_deep_live,
    is_protected_job_domain,
)
from backend.tests.fixtures import FIXTURE_RESUME


class DeepSearchExtractionTest(unittest.TestCase):
    def test_extracts_json_ld_job_posting_from_public_page(self):
        html = '''
        <html><head><title>Senior AI Engineer - Acme</title>
        <script type="application/ld+json">{
          "@context": "https://schema.org",
          "@type": "JobPosting",
          "title": "Senior AI Engineer",
          "description": "Build generative AI products with Python, TypeScript, React, retrieval, and APIs. Visa sponsorship available in Germany.",
          "datePosted": "2026-05-20",
          "hiringOrganization": {"name": "Acme AI"},
          "jobLocation": {"address": {"addressLocality": "Berlin", "addressCountry": "Germany"}},
          "applicantLocationRequirements": {"name": "Germany"}
        }</script></head><body></body></html>
        '''

        job = _extract_job_from_html('https://jobs.example.com/senior-ai', html, 'brave', 'Brave Search', '2026-05-27T00:00:00Z')

        self.assertIsNotNone(job)
        self.assertEqual(job.title, 'Senior AI Engineer')
        self.assertEqual(job.company, 'Acme AI')
        self.assertIn('Berlin', job.location)
        self.assertEqual(job.country, 'Germany')
        self.assertEqual(job.visa_sponsorship, 'yes')
        self.assertIn('generative AI products', job.description)

    def test_extracts_visible_job_page_when_json_ld_is_absent(self):
        html = '''
        <html><head><title>Backend Engineer at Northstar Labs</title></head>
        <body>
          <nav>Careers Home Benefits</nav>
          <main>
            <h1>Backend Engineer</h1>
            <section>Northstar Labs</section>
            <p>Location: Dublin, Ireland Remote</p>
            <p>We are hiring a backend engineer to build Python APIs, distributed systems, PostgreSQL data models, and observability tooling.</p>
            <p>Visa sponsorship can be considered for strong candidates.</p>
          </main>
        </body></html>
        '''

        job = _extract_job_from_html('https://careers.example.com/jobs/backend', html, 'deep', 'Deep Live Search', '2026-05-27T00:00:00Z')

        self.assertIsNotNone(job)
        self.assertEqual(job.title, 'Backend Engineer')
        self.assertIn('Python APIs', job.description)
        self.assertEqual(job.remote, 'yes')
        self.assertEqual(job.visa_sponsorship, 'yes')


class DeepSourceTest(unittest.TestCase):
    def test_protected_job_domains_are_not_crawled(self):
        self.assertTrue(is_protected_job_domain('https://www.linkedin.com/jobs/view/123'))
        self.assertTrue(is_protected_job_domain('https://www.naukri.com/job-listings-python-engineer'))
        self.assertTrue(is_protected_job_domain('https://www.instahyre.com/job-123'))
        self.assertFalse(is_protected_job_domain('https://boards.greenhouse.io/acme/jobs/123'))

    def test_deep_live_filters_public_feed_results_by_query(self):
        remoteok_payload = [
            {'legal': 'ok'},
            {
                'id': 1,
                'position': 'Generative AI Engineer',
                'company': 'Acme AI',
                'location': 'Remote Europe',
                'description': 'Build generative AI systems with Python, TypeScript, and retrieval APIs.',
                'url': 'https://remoteok.com/remote-jobs/1-generative-ai-engineer',
                'tags': ['python', 'ai'],
                'date': '2026-05-20T00:00:00+00:00',
            },
            {
                'id': 2,
                'position': 'Product Designer',
                'company': 'Design Co',
                'location': 'Remote',
                'description': 'Design systems and Figma prototypes.',
                'url': 'https://remoteok.com/remote-jobs/2-product-designer',
                'tags': ['design'],
            },
        ]

        def fake_json(url):
            if 'remoteok.com' in url:
                return remoteok_payload
            if 'arbeitnow.com' in url:
                return {'data': []}
            if 'remotive.com' in url:
                return {'jobs': []}
            return {}

        prefs = SearchPreference(query='generative ai engineer', region='eu_uk', countries=['Germany', 'United Kingdom'], sources=['deep'])
        with patch('backend.services.sources._read_json', side_effect=fake_json), patch('backend.services.sources._read_text', return_value=''):
            result = fetch_deep_live(prefs)

        self.assertEqual(result.source_id, 'deep')
        self.assertEqual([job.title for job in result.jobs], ['Generative AI Engineer'])
        self.assertIn('RemoteOK', result.status.message)

    def test_deep_source_is_used_by_live_search(self):
        deep_jobs = []

        def fake_deep(preferences):
            from backend.tests.fixtures import MATCHING_JOB
            deep_jobs.append(preferences.query)
            job = MATCHING_JOB
            job.source_id = 'deep'
            job.source_name = 'Deep Live Search'
            return SourceResult('deep', [job], result_status('deep'))

        def result_status(source_id):
            from backend.services.models import SourceStatus
            return SourceStatus(source_id, 'available', 'ok')

        response = search_jobs(FIXTURE_RESUME, SearchPreference(query='full stack engineer', region='eu_uk', sources=['deep']), sources=[fake_deep])

        self.assertEqual(deep_jobs, ['full stack engineer'])
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].job.source_id, 'deep')


if __name__ == '__main__':
    unittest.main()
