import unittest

from backend.services.models import SearchPreference
from backend.services.regions import normalize_region
from backend.services.sources import official_company_sources, seeded_source


class SourceConnectorTest(unittest.TestCase):
    def test_seeded_source_varies_by_query_and_region(self):
        india = SearchPreference(query='product manager', region='india', countries=normalize_region({'region': 'india'}).countries)
        eu = SearchPreference(query='backend engineer', region='eu_uk', countries=normalize_region({'region': 'eu_uk'}).countries)

        india_jobs = seeded_source(india).jobs
        eu_jobs = seeded_source(eu).jobs

        self.assertNotEqual([job.title for job in india_jobs], [job.title for job in eu_jobs])
        self.assertTrue(any(job.country == 'India' for job in india_jobs))

    def test_official_company_sources_include_ats_and_career_hints(self):
        sources = official_company_sources(['bmw', 'example-greenhouse'])

        self.assertTrue(any(source.source_id.startswith('official:bmw') for source in sources))
        self.assertTrue(any('Greenhouse' in source.name or 'careers' in source.name.lower() for source in sources))


if __name__ == '__main__':
    unittest.main()
