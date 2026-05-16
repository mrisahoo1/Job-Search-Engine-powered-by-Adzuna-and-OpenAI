import unittest

from backend.services.regions import normalize_region, region_options


class RegionTest(unittest.TestCase):
    def test_defaults_to_eu_plus_uk(self):
        region = normalize_region({})

        self.assertEqual(region.id, 'eu_uk')
        self.assertIn('Germany', region.countries)
        self.assertIn('United Kingdom', region.countries)

    def test_supports_india_us_australia_and_remote_global(self):
        ids = {region.id for region in region_options()}

        self.assertTrue({'eu_uk', 'india', 'us', 'australia', 'remote_global'}.issubset(ids))
        self.assertIn('India', normalize_region({'region': 'india'}).countries)
        self.assertIn('United States', normalize_region({'region': 'us'}).countries)
        self.assertIn('Australia', normalize_region({'region': 'australia'}).countries)


if __name__ == '__main__':
    unittest.main()
