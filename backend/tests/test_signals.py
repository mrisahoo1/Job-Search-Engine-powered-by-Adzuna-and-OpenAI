import unittest

from backend.services.signals import detect_country, detect_remote_signal, detect_visa_signal


class SignalDetectionTest(unittest.TestCase):
    def test_detects_positive_remote_and_visa_signals(self):
        text = 'Remote first team based in Berlin. Visa sponsorship and relocation support available.'

        self.assertEqual(detect_remote_signal(text), 'yes')
        self.assertEqual(detect_visa_signal(text), 'yes')

    def test_negative_sponsorship_is_not_positive(self):
        self.assertEqual(detect_visa_signal('Applicants must already have work authorization. No visa sponsorship.'), 'no')

    def test_detects_eu_country_names(self):
        self.assertEqual(detect_country('Amsterdam, Netherlands'), 'Netherlands')
        self.assertEqual(detect_country('Remote - Germany'), 'Germany')

    def test_detects_uk_location_aliases(self):
        self.assertEqual(detect_country('Farnborough, Hampshire'), 'United Kingdom')
        self.assertEqual(detect_country('London, UK'), 'United Kingdom')
        self.assertEqual(detect_country('Widnes, Cheshire'), 'United Kingdom')

    def test_detects_supported_non_eu_regions(self):
        self.assertEqual(detect_country('Bengaluru, India'), 'India')
        self.assertEqual(detect_country('NYC, New York'), 'United States')
        self.assertEqual(detect_country('Sydney, Australia'), 'Australia')


if __name__ == '__main__':
    unittest.main()
